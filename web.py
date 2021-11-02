from os import stat
import time
from flask import Flask, url_for, request, Response, make_response
import RPi.GPIO as GPIO
import os.path
import json

# Custom modules
import config
import utils

fileName = os.path.basename(__file__)

utils.logger("Hello from Web service!", fileName)
utils.logger("Setting up GPIO Pins", fileName)

# Use BOARD mode. The pin numbers refer to the **BOARD** connector not the chip.
# @see https://pinout.xyz/pinout/3v3_power# and the smaller numbers next to the PINs
# in the graph
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Set up the PINs as an input with a pull-up resistor.
# These will monitor door state.
GPIO.setup(config.SWITCH_UPPER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(config.SWITCH_LOWER, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Setup OPEN & CLOSE relay control. The output
# must be set right after in order to the relay not
# be set with a wrong value (LOW).
GPIO.setup(config.PINS_BUTTON_OPEN, GPIO.OUT)
GPIO.output(config.PINS_BUTTON_OPEN, GPIO.HIGH)
if config.PINS_BUTTON_OPEN != config.PINS_BUTTON_CLOSE:
    GPIO.setup(PINS_BUTTON_CLOSE, GPIO.OUT)
    GPIO.output(PINS_BUTTON_CLOSE, GPIO.HIGH)

utils.logger("Setting up GPIO Pins ... done!", fileName)

# With static_url_path Flask serves all assets under the /static
# with no further configuration.
app = Flask(__name__, static_url_path='/static')


passwd_file = 'garage-password.txt'
cwd = os.path.dirname(os.path.abspath(__file__))
file = os.path.join(cwd, passwd_file)
if os.path.isfile(file):
    utils.logger("Using passwd from a file: " + file)
    # Reads all of the content without newlines into a password.
    with open(file) as f:
        OpenTriggerPassword = f.read().splitlines()[0]
else:
    utils.logger("Passwd file was not found:" + file +
                 ". Using default passwd.", fileName)


# Fetch user real IP even if flask is running behind proxy.
def user_ip_address():
    user_ip = ''
    if 'X-Forwarded-For' in request.headers:
        user_ip = request.remote_addr + ', ' + \
            request.headers['X-Forwarded-For']
    else:
        user_ip = request.remote_addr  # For local development
    return user_ip


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
    user_ip = user_ip_address()
    logger("Request from IP " + user_ip, fileName)
    return app.send_static_file('index.html')


# REST API, /door endpoint
@app.route('/api/door', methods=['GET'])
def api():
    status = utils.door_status()

    response = {
        'status': status if status != None else None,
        'color': None,
        'image': None,
    }
    if status == 'in-between':
        response['color'] = 'orange'
        response['image'] = 'GarageQuestion.gif'
    elif status == 'closed':
        response['color'] = 'green'
        response['image'] = 'GarageGreen.gif'
    elif status == 'opened':
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
    user_ip = user_ip_address()
    status = utils.door_status()
    name = request.form['garagecode']
    # the Password that Opens Garage Door (Code if Password is Correct)
    if name == OpenTriggerPassword:
        utils.logger(
            "Triggered Opening/Closing (IP: " + user_ip + ")", fileName)
        # This triggers the Opening/Closing the door.
        if status == 'opened':
            GPIO.output(config.PINS_BUTTON_CLOSE, GPIO.LOW)
            time.sleep(.5)
            GPIO.output(config.PINS_BUTTON_CLOSE, GPIO.HIGH)
        elif status == 'closed':
            GPIO.output(config.PINS_BUTTON_OPEN, GPIO.LOW)
            time.sleep(.5)
            GPIO.output(config.PINS_BUTTON_OPEN, GPIO.HIGH)
        elif status == 'in-between':
            GPIO.output(config.PINS_BUTTON_CLOSE, GPIO.LOW)
            time.sleep(.5)
            GPIO.output(config.PINS_BUTTON_CLOSE, GPIO.HIGH)

        utils.logger("Triggered Opening/Closing completed.", fileName)
        headers = dict()
        headers['Location'] = url_for('index')
        return Response(
            'Button pressed.', 304, headers)

    else:
        utils.logger(
            "Wrong password provided, request originated from IP " + user_ip, fileName)
        return Response(
            'Wrong password - no access.', 401)


@app.route('/log')
def logfile():
    user_ip = user_ip_address()
    utils.logger("Access to route /Log from IP " + user_ip), fileName
    return app.send_static_file('log.txt')


if __name__ == '__main__':
    #     app.run(debug=True, host='0.0.0.0', port=5000)
    app.run(host='0.0.0.0', port=5000)
