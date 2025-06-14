import os.path, threading, datetime
from datetime import datetime
import requests
from dotenv import dotenv_values

# Load .env files
config = {
    **dotenv_values(".env.default"),  # load what came with the repo
    **dotenv_values(".env"),  # load overrides from the local
}
fileName = os.path.basename(__file__)

for k, v in config.items():
    if v == 'False':
        config[k] = False
    elif v == 'True':
        config[k] = True
if "DEGUG" in config or config["DEBUG"] == True or config["DEBUG"] == None:
    print("Config in ${fileName}: ")
    for k, v in config.items():
        print(str(k) + " => [" + str(type(v)) + "] " + str(v))



API_CONTROLLER = "http://127.0.0.1:" + config["API_CONTROLLER_PORT"]
API_LOGGER = "http://127.0.0.1:" + config["API_LOGGER_PORT"]

# APIs, Logger API
def logger(msg):
    if type(msg) == str and len(msg) > 0:
        payload = dict(log_entry=msg, source=fileName)
        resp = requests.post( f"{API_LOGGER}/new", timeout=2, data=payload)
        return resp.status_code == 200
    return False

# APIs, Controller API
def getStatus():
    try:
        resp = requests.get( f"{API_CONTROLLER}/status", timeout=2)
        return resp.json().get("door", '')
    except Exception as e:
        logger("WebUtils getStatus() received from Controller API: " + str(e))
        return None

# APIs, Controller API
def openDoor():
    try:
        resp = requests.get( f"{API_CONTROLLER}/open", timeout=2)
        return resp.json().get("door", '')
    except Exception as e:
        logger("WebUtils openDoor() received from Controller API: " + str(e))
        return None

# APIs, Controller API
def closeDoor():
    try:
        resp = requests.get( f"{API_CONTROLLER}/close", timeout=2)
        return resp.json().get("door", '')
    except Exception as e:
        logger("WebUtils closeDoor() received from Controller API: " + str(e))
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
    return config["DoorPassword"]
