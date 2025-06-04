import os.path, requests, json, logging
from flask import Flask, url_for, request, Response, make_response

import config
from utils import logger, user_ip_address, get_door_pwd

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
        return 'Failed'


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug={config.DEBUGGING})
