import time
from datetime import datetime
from flask import Flask, render_template, request, Response

import RPi.GPIO as GPIO
# the pin numbers refer to the board connector not the chip
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
# set up pin ?? (one of the above listed pins) as an input with a pull-up resistor
GPIO.setup(16, GPIO.IN, GPIO.PUD_UP)
# set up pin ?? (one of the above listed pins) as an input with a pull-up resistor
GPIO.setup(18, GPIO.IN, GPIO.PUD_UP)
# GPIO.setup(7, GPIO.OUT)
# GPIO.output(7, GPIO.HIGH)
GPIO.setup(11, GPIO.OUT)
GPIO.output(11, GPIO.HIGH)
# GPIO.setup(13, GPIO.OUT)
# GPIO.output(13, GPIO.HIGH)
# GPIO.setup(15, GPIO.OUT)
# GPIO.output(15, GPIO.HIGH)

# Wtih static_url_path Flask serves all assets under the /static
# with no further configuration.
app = Flask(__name__, static_url_path='/static')

OpenTriggerPassword = "12345678"
VerboseConsole = False  # Wether or not print messages to console as well.

# Fetch user real IP even if flask is running behind proxy.


def logger(msg):
    logfile = open("/home/pi/GarageWeb/static/log.txt", "a")
    logfile.write(datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S [web.py] -- " + msg + "\n"))
    logfile.close()
    if VerboseConsole == True:
        print(msg)

# Fetch user real IP even if flask is running behind proxy.


def user_ip_address():
    user_ip = ''
    if 'X-Forwarded-For' in request.headers:
        proxy_data = request.headers['X-Forwarded-For']
        ip_list = proxy_data.split(',')
        user_ip = ip_list[0]  # first address in list is User IP
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

# Main route for GET requests.


@app.route('/', methods=['GET'])
def index():
    user_ip = user_ip_address()
    if GPIO.input(16) == GPIO.HIGH and GPIO.input(18) == GPIO.HIGH:
        logger("(web) Garage is Opening/Closing")
        return app.send_static_file('Question.html')
    else:
        if GPIO.input(16) == GPIO.LOW:
            logger("(web) Garage is Closed")
            return app.send_static_file('Closed.html')
        if GPIO.input(18) == GPIO.LOW:
            logger("(web) Garage is Open")
            return app.send_static_file('Open.html')

# Main route for POST requests (ie. door open/close requests)


@app.route('/', methods=['POST'])
def Garage():
    user_ip = user_ip_address()
    name = request.form['garagecode']
    # the Password that Opens Garage Door (Code if Password is Correct)
    if name == OpenTriggerPassword:
        logger("Garage web triggered Opening/Closing (IP: " + user_ip + ")")
        # This triggers the Opening/Closing the door.
        GPIO.output(11, GPIO.LOW)
        time.sleep(.5)
        GPIO.output(11, GPIO.HIGH)
        logger("Garage web triggered Opening/Closing completed.")
        time.sleep(2)
        return app.redirect('/', 200)

    else:
        logger("Wrong password provided, request originated from IP " + user_ip)
        return app.redirect('/', 400)


@app.route('/Log')
def logfile():
    user_ip = user_ip_address()
    logger("Access to route /Log from IP " + user_ip)
    return app.send_static_file('log.txt')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

except KeyboardInterrupt:
    logger("Web UI Shutdown -- Goodbye!")
    GPIO.cleanup()
