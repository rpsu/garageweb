import RPi.GPIO as GPIO
from datetime import datetime
import time
import config
import os.path

fileName = os.path.basename(__file__)


def logger(msg, fileName='??'):
    logfile = open("/home/pi/GarageWeb/static/log.txt", "a")
    logfile.write(datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S [" + fileName + "] - - " + msg + "\n"))
    logfile.close()
    if config.VerboseConsole == True:
        print(msg)


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
        return config.DoorPassword
