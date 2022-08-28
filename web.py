from fileinput import filename
from os import stat
import time
from datetime import datetime
from flask import Flask, url_for, request, Response, make_response
import RPi.GPIO as GPIO
import os.path
import json
import config
from utils import logger, user_ip_address
import doorControls

fileName = os.path.basename(__file__)


logger('Hello from Web service!', fileName)

doorControls.setup(fileName)

# With static_url_path Flask serves all assets under the /static
# with no further configuration.
app = Flask(__name__, static_url_path='/static')


passwd_file = 'garage-password.txt'
cwd = os.path.dirname(os.path.abspath(__file__))
file = os.path.join(cwd, passwd_file)
if os.path.isfile(file):
    logger("Using passwd from a file: " + file, fileName)
    # Reads all of the content without newlines into a password.
    with open(file) as f:
        config.OpenTriggerPassword = f.read().splitlines()[0]
else:
    logger("Passwd file was not found:" + file +
           ". Using default passwd.", fileName)


# Prevent all responses from being cached.
@app.after_request
def add_header(resp):
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    resp.headers['Cache-Control'] = 'public, max-age=0'
    return resp


# Main route for GET requests
@app.route('/', methods=['GET'])
def index():
    user_ip = user_ip_address(request)
    logger("Request from IP " + user_ip, fileName)
    return app.send_static_file('index.html')


# REST API, /door endpoint
@app.route('/api/door', methods=['GET'])
def api():
    status = doorControls.status()

    response = {
        'status': status if status != None else None,
        'color': None,
        'image': None,
    }
    if status == config.STATE_BETWEEN:
        response['color'] = 'orange'
        response['image'] = 'GarageQuestion.gif'
    elif status == config.STATE_DOWN:
        response['color'] = 'green'
        response['image'] = 'GarageGreen.gif'
    elif status == config.STATE_UP:
        response['color'] = 'red'
        response['image'] = 'GarageRed.gif'
    else:
        logger('** ALERT ** Unknown door status response: ' + status, fileName)

    resp = make_response(json.dumps(response))
    resp.headers['Content-Type'] = 'application/json'

    return resp

# Main route for POST requests (ie. door open/close requests)


@ app.route('/', methods=['POST'])
def openTheDoorPlease():
    user_ip = user_ip_address(request)
    status = doorControls.status()
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
        if status == config.STATE_UP:
            doorControls.close(fileName)
        elif status == config.STATE_DOWN:
            doorControls.open(fileName)
        elif status == config.STATE_BETWEEN:
            doorControls.close(fileName)

        logger("Door action completed.", fileName)
        headers = dict()
        headers['Location'] = url_for('index')
        return Response(
            'Button pressed.', 304, headers)


@ app.route('/log')
def logfile():
    logger("Access to route /Log from IP " +
           user_ip_address(request), fileName)
    return app.send_static_file('log.txt')


if __name__ == '__main__':
    #     app.run(debug=True, host='0.0.0.0', port=5000)
    app.run(host='0.0.0.0', port=5000)
