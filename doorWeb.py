import os.path, json, re
from flask import Flask, url_for, request, Response, make_response, redirect
from dotenv import dotenv_values

from webUtils import logger, user_ip_address, get_door_pwd, getStatus, openDoor, closeDoor, toggleDoor

# Load .env files
dir = os.path.dirname(__file__) + "/"
fileName = os.path.basename(__file__)
config = {
    **dotenv_values(dir + ".env.default"),  # load what came with the repo
    **dotenv_values(dir + ".env"),  # load overrides from the local
}

for k, v in config.items():
    if v == 'False':
        config[k] = False
    elif v == 'True':
        config[k] = True
    elif re.search("\d", config.get(k)) is not None:
        config[k] = int(config[k])

debug = config.get("DEBUG", False)

if debug:
    print("Config in ${fileName}: ")
    for k, v in config.items():
        print(str(k) + " => [" + str(type(v)) + "] " + str(v))

API_CONTROLLER = "http://127.0.0.1:" + str(config.get("API_CONTROLLER_PORT"))

# Door state constants.
STATE_UP = config.get("STATE_UP")
STATE_DOWN = config.get("STATE_DOWN")
STATE_BETWEEN = config.get("STATE_BETWEEN")

# With static_url_path Flask serves all assets under the /static
# with no further configuration.
app = Flask(__name__, static_url_path='/static')
listen_to_ip = '0.0.0.0'
listen_to_port = str(config.get("API_WEB_PORT"))

# Routes are in webUtils.

# Prevent all responses from being cached.
@app.after_request
def add_header(resp):
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
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
@ app.route('/', methods=['POST'])
def openTheDoorPlease():
    # the Password that Opens Garage Door (Code if Password is Correct)
    user_ip = user_ip_address(request)
    name = request.form['password']
    if name != get_door_pwd():
        logger("Wrong password provided, request originated from IP " +
               user_ip)
        return Response(
            'Wrong password - no access.', 401)

    logger("Triggered Opening/Closing (IP: " + user_ip + ")")

    # This triggers the Opening/Closing the door.
    status = getStatus()
    if status == STATE_UP:
        closeDoor()
    elif status == STATE_DOWN:
        openDoor()
    elif status == STATE_BETWEEN:
        toggleDoor()

    logger("Door action triggered. The door may still be closing or opening.")
    # The app runs behind a proxy so the full URLs need to be forced to HTTPS scheme.
    return redirect(url_for('index', _external=True, _scheme='https'))

# Routes, API endpoint /log endpoint
@ app.route('/log')
def logfile():
    logger("Access to route /Log from IP " +
           user_ip_address(request))
    return app.send_static_file('log.txt')


if __name__ == '__main__':
    msg = f'Hello from {fileName} '
    msg = msg + "(debug: " + str(debug) + ")!"
    logger(msg)
    app.run(host=listen_to_ip, port=listen_to_port, debug="${debug}" )
