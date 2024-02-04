import json
import os
import platform
from flask import Flask, Response, redirect, request, make_response
from multiprocessing import Process
from utils import logger, user_ip_address
from config import FlaskDebug, FlaskPort
from door import closeTheDoor, getTheDoorStatus, openTheDoor
from doorMonitor import run
import config
import argparse
import atexit

# Allow overwriting of some of the config values from the command line
parser = argparse.ArgumentParser()
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()

if args.debug is not None:
  FlaskDebug = args.debug

app = Flask(__name__)
fileName = os.path.basename(__file__)
logger('fileName: ' + fileName, fileName, 2)
currentFolder = os.path.dirname(__file__)
logger('currentFolder: ' + currentFolder, fileName, 2)
# Get the poetry project root directory

logFilePath = currentFolder + "/static/log.txt"
passwd_file = currentFolder + '/../garage-password.txt'

if os.path.isfile(passwd_file):
    logger("Passwd from a file: " + passwd_file, fileName, 0)
    # Reads all of the content without newlines into a password.
    with open(passwd_file) as f:
        config.OpenTriggerPassword = f.read().splitlines()[0]
else:
    logger("Passwd file was not found:" + passwd_file +
           ". Using default passwd.", fileName, 0)


logger('Hello from Web service!', fileName, 0)

# Main route for GET requests
@app.route('/', methods=['GET'])
def index():
  user_ip = user_ip_address(request)
  logger("Request from IP " + user_ip, fileName)
  return app.send_static_file('index.html')


# REST API, /door endpoint
@app.route('/api/door', methods=['GET'])
def api():
  doorStatus = getTheDoorStatus()
  logger("route('/api/door') has doorStatus: " + doorStatus, fileName, 2)
  if doorStatus == config.STATE_BETWEEN:
    response = 'between'
  elif doorStatus == config.STATE_DOWN:
    response = 'closed'
  elif doorStatus == config.STATE_UP:
    response = 'opened'
  else:
    logger('** ALERT ** Unknown door status response: ' + doorStatus, fileName)

  resp = make_response(json.dumps(response))
  resp.headers['Content-Type'] = 'application/json'

  return resp

@app.route('/log', methods=['GET'])
def log():
  global currentFolder
  logFileLocation= currentFolder + '/static/log.txt'
  logger("route('/log') has logFileLocation: " + logFileLocation, fileName, 2)
  try:
    with open(logFileLocation, 'r') as f:
      lines = f.readlines()
      last_20_lines = lines[-20:]
    return '<br>'.join(last_20_lines)
  except FileNotFoundError:
    return "The log file does not exist."

@ app.route('/api/toggle', methods=['POST'])
def openTheDoorPlease():
    user_ip = user_ip_address(request)
    name = request.form['garagecode']
    # the Password that Opens Garage Door (Code if Password is Correct)
    if name != config.OpenTriggerPassword:
        logger("Wrong password provided, request originated from IP " +
               user_ip, fileName)
        return Response(
            'Wrong password - no access.', 401)

    else:
        logger("Triggered Opening/Closing (IP: " + user_ip + ")", fileName)
        # This triggers the Opening/Closing the door.
        if getTheDoorStatus == config.STATE_UP:
            closeTheDoor(fileName)
        elif getTheDoorStatus == config.STATE_DOWN:
            openTheDoor(fileName)
        elif getTheDoorStatus == config.STATE_BETWEEN:
            closeTheDoor(fileName)

        logger("Door action completed.", fileName)
        return redirect('/')

def run_door_monitor():
  run()  # Start the door monitor

def cleanup():
  global door_monitor_process
  logger("Cleaning up...", fileName, 0)
  door_monitor_process.terminate()
  door_monitor_process.join()


if __name__ == '__main__':
  # Start the door monitor in a separate process
  global door_monitor_process
  door_monitor_process = Process(target=run_door_monitor)
  door_monitor_process.start()

  # Register the cleanup function to be called when the program exits
  atexit.register(cleanup)

  # config.py contains the following configuration:

  if platform.machine() == 'armv7l':
      logger("Door code seems to run on Raspi.", fileName, 2)
      app.run(debug=FlaskDebug, host='0.0.0.0', port=FlaskPort)
      # We are not on macOS
  else:
      logger("Door code seems to run on MacOS.", fileName, 2)
      # We are on macOS so let's use local SSL certificates.
      app.run(debug=FlaskDebug, host='0.0.0.0', port=FlaskPort, ssl_context=(currentFolder + '/certs/cert.pem', currentFolder + '/certs/key.pem'))
