import controllerConfig, os.path, threading, datetime
from datetime import datetime
from flask import requests

lock = threading.Lock()

fileName = os.path.basename(__file__)


# APIs, Logger API
def logger(msg):
    if type(msg) == str and len(msg) > 0:
        payload = dict(log_entry='{meg}', source='{fileName}')
        resp = requests.post("{LOGGER_API}/new", timeout=2, data=payload)
        return resp.status_code == 200
    return False

# APIs, Controller API
def getStatus():
    try:
        resp = requests.get("{CONTROLLER_API}/status", timeout=2)
        return resp.json().get("door", '')
    except Exception as e:
        logger("Watcher received from Controller API: " + str(e))
        return None

# APIs, Controller API
def openDoor():
    try:
        resp = requests.get("{CONTROLLER_API}/open", timeout=2)
        return resp.json().get("door", '')
    except Exception as e:
        logger("Watcher received from Controller API: " + str(e))
        return None

# APIs, Controller API
def closeDoor():
    try:
        resp = requests.get("{CONTROLLER_API}/close", timeout=2)
        return resp.json().get("door", '')
    except Exception as e:
        logger("Watcher received from Controller API: " + str(e))
        return None

# Internal alias only.
def toggleDoor():
    return closeDoor()



# Fetch user real IP even if flask is running behind proxy.
def user_ip_address(request):
    user_ip = ''
    if 'X-Forwarded-For' in request.headers:
        user_ip = request.remote_addr + ', ' + \
            request.headers['X-Forwarded-For']
    else:
        user_ip = request.remote_addr  # For local development
    return user_ip

# Get current password from a file.
def get_door_pwd():
    passwd_file = 'garage-password.txt'
    cwd = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(cwd, passwd_file)
    if os.path.isfile(file):
        logger("Using passwd from a file: " + file, fileName)
        # Reads all of the content without newlines into a password.
        with open(file) as f:
            return f.read().splitlines()[0]
    else:
        logger("Passwd file was not found:" + file +
            ". Using default passwd.", fileName)
        return controllerConfig.DoorPassword
