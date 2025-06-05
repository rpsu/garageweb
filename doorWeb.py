import os.path, json
from flask import Flask, url_for, request, Response, make_response

from webUtils import logger, user_ip_address, get_door_pwd, getStatus, openDoor, closeDoor, toggleDoor

fileName = os.path.basename(__file__)
API_CONTROLLER = "http://127.0.0.1:5080"
debug = True

# Door state constants.
STATE_UP = 'up'
STATE_DOWN = 'down'
STATE_BETWEEN = 'between'

# With static_url_path Flask serves all assets under the /static
# with no further configuration.
app = Flask(__name__, static_url_path='/static')
listen_to_ip = '0.0.0.0'
listen_to_port = 5000

# Routes are in webUtils.

# Prevent all responses from being cached.
@app.after_request
def add_header(resp):
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    resp.headers['Cache-Control'] = 'public, max-age=0'
    return resp


# Routes, Main route for GET requests
@app.route('/', methods=['GET'])
def index():
    user_ip = user_ip_address(request)
    logger("Request from IP " + user_ip)
    return app.send_static_file('index.html')


# Routes, API endpoint /door endpoint
@app.route('/api/door', methods=['GET'])
def restApiDoor():
    response = {
        'status': None,
        'color': None,
        'image': None,
    }
    try:
        status = getStatus()

        response['status' ] = status if status != None else None

        if status == STATE_BETWEEN:
            response['color'] = 'orange'
            response['image'] = 'GarageQuestion.gif'
        elif status == STATE_DOWN:
            response['color'] = 'green'
            response['image'] = 'GarageGreen.gif'
        elif status == STATE_UP:
            response['color'] = 'red'
            response['image'] = 'GarageRed.gif'
        else:
            logger('** ALERT ** Unknown door status response: ' + status)
        logger("API response is " + json.dumps(response))
        resp = make_response(json.dumps(response))
        resp.headers['Content-Type'] = 'application/json'

        return resp

    except Exception as e:
        logger("API response threw an Exception " + str(e))
        result = {"error": "status retrieval error", "code": 500}
        result['detail'] = str(e)
        return json.dumps(result), 500


# Main route for POST requests (ie. door open/close requests)
# Routes, API endpoint POST /api/toggle endpoint
@ app.route('/api/toggle', methods=['POST'])
def openTheDoorPlease():
    # the Password that Opens Garage Door (Code if Password is Correct)
    user_ip = user_ip_address(request)
    name = request.form['garagecode']
    if name != get_door_pwd():
        logger("Wrong password provided, request originated from IP " +
               user_ip)
        return Response(
            'Wrong password - no access.', 401)

    logger("Triggered Opening/Closing (IP: " + user_ip + ")")

    # This triggers the Opening/Closing the door.
    status = getStatus()
    if status == STATE_UP:
        closeDoor(fileName)
    elif status == STATE_DOWN:
        openDoor(fileName)
    elif status == STATE_BETWEEN:
        toggleDoor(fileName)

    logger("Door action triggered. The door may still be closing or opening.")
    headers = dict()
    headers['Location'] = url_for('index')
    return Response(
        'Button pressed.', 304, headers)


# Routes, API endpoint /log endpoint
@ app.route('/log')
def logfile():
    logger("Access to route /Log from IP " +
           user_ip_address(request))
    return app.send_static_file('log.txt')


if __name__ == '__main__':
    msg= 'Hello from {fileName} '
    msg=msg + "(debug: " + str(debug) + ")!"
    logger(msg)
    app.run(host={listen_to_ip}, port={listen_to_port}, debug={debug})
