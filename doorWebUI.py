import os.path, requests, json, logging, time, datetime, threading, math
from flask import Flask, url_for, request, Response, make_response

import config
from utils import logger, user_ip_address, get_door_pwd
import doorControls

lock = threading.Lock()

fileName = os.path.basename(__file__)
SERVICE_REST_API = "http://127.0.0.1:8088"

logger('Hello from doorWebUI. Serving HTML!', fileName)

# With static_url_path Flask serves all assets under the /static
# with no further configuration.
app = Flask(__name__, static_url_path='/static')

# Configure Flask logging mainly for the UTF-8 filesystem.
logging.basicConfig(
    format='%(asctime)s %(levelname)s [%(module)s] %(message)s',
    level=logging.INFO,
    datefmt='%a, %d %b %Y %H:%M:%S',
    encoding='utf-8'
)
if config.DEBUGGING:
    logging.basicConfig(level=logging.DEBUG)

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
def restApiDoor():
    response = {
        'status': None,
        'color': None,
        'image': None,
    }
    try:
        status = requests.get("%s/status" % SERVICE_REST_API, timeout=2)
        response['status' ] = status if status != None else None

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
        logger("API response is " + json.dumps(response), fileName)
        resp = make_response(json.dumps(response))
        resp.headers['Content-Type'] = 'application/json'

        return resp

    except Exception as e:
        logger("API response threw an Exception " + str(e), fileName)
        result = {"error": "status retrieval error", "code": 500}
        result['detail'] = str(e)
        return json.dumps(result), 500


# Main route for POST requests (ie. door open/close requests)


@ app.route('/api/toggle', methods=['POST'])
def openTheDoorPlease():
    # the Password that Opens Garage Door (Code if Password is Correct)
    user_ip = user_ip_address(request)
    name = request.form['garagecode']
    if name != get_door_pwd():
        logger("Wrong password provided, request originated from IP " +
               user_ip, fileName)
        return Response(
            'Wrong password - no access.', 401)

    logger("Triggered Opening/Closing (IP: " + user_ip + ")", fileName)
    status = requests.get("%s/toggle" % SERVICE_REST_API, timeout=2)


    logger("Door action completed. The door may still be closing or opening.", fileName)
    headers = dict()
    headers['Location'] = url_for('index')
    return Response(
        'Button pressed.', 304, headers)


@ app.route('/log')
def logfile():
    logger("Access to route /Log from IP " +
           user_ip_address(request), fileName)
    return app.send_static_file('log.txt')

# Read door status from magnetic switches connected to GPIO
def doorMonitor():

    DoorOpenTimer = 0  # Default start status turns timer off
    DoorOpenTimerMessageSent = 1  # Turn off messages until timer is started

    while True:
        with lock:
            TimeDoorOpened = datetime.datetime.now()
            # Start the timer if door is open at the boot time.
            if doorControls.status() == config.STATE_UP:  # Door is Open
                logger("Door is Open and timer is running (started " + str(TimeDoorOpened) + ".", fileName)
                DoorOpenTimer = 1
            else:
                DoorOpenTimer = 0
            time.sleep(5)
             # Door Open Timer has Started
            if DoorOpenTimer == 1:
                logger("Door timer is ON with delay of " +
                    str(math.floor(config.DoorOpenMessageDelay/60)) + " minutes. Door is " + doorControls.status() + ".", fileName)

                currentTimeDate = datetime.datetime.now()

                if (currentTimeDate - TimeDoorOpened).total_seconds() > config.DoorOpenMessageDelay and DoorOpenTimerMessageSent == 0:
                    logger("Your Garage Door has been Open for " +
                        str(math.floor(config.DoorOpenMessageDelay/60)) + " minutes", fileName)
                    DoorOpenTimerMessageSent = 1

                if (currentTimeDate - TimeDoorOpened).total_seconds() > config.DoorAutoCloseDelay and DoorOpenTimerMessageSent == 1:
                    logger("Closing Garage Door automatically now since it has been left Open for  " +
                        str(math.floor(config.DoorAutoCloseDelay/60)) + " minutes", fileName)
                    doorControls.close(fileName)
                    DoorOpenTimer = 0

            # Door Status is Unknown
            if doorControls.status() == config.STATE_BETWEEN:
                logger("Door Opening/Closing", fileName)
                while doorControls.status() == config.STATE_BETWEEN:
                    time.sleep(10)

                else:
                    if doorControls.status() == config.STATE_DOWN:
                        logger("Door Closed", fileName)
                        DoorOpenTimer = 0

                    elif doorControls.status() == config.STATE_UP:
                        # Start Door Open Timer
                        TimeDoorOpened = datetime.datetime.now()
                        logger("Door opened fully: " +
                            str(TimeDoorOpened), fileName)
                        DoorOpenTimer = 1
                        DoorOpenTimerMessageSent = 0


if __name__ == '__main__':
    doorControls.setup(fileName)
    thread = threading.Thread(target=doorMonitor)
    thread.daemon = True  # Make this thread a daemon
    thread.start()

    app.run(host='0.0.0.0', port=5000, debug={config.DEBUGGING})
