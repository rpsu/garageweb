from datetime import datetime
import config
import platform


import os.path
# Directory of this file, no trailing slash.
currentFolder = os.path.dirname(__file__)

def logger(msg, fileName, level=1):
    logFilePath = currentFolder + "/static/log.txt"
    if level <= config.LogLevel:
        logfile = open(logFilePath, "a")
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
