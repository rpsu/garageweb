import atexit, signal, time, controllerConfig, os.path, threading, requests, datetime
import RPi.GPIO as GPIO
from flask import Flask, json, jsonify

debug=controllerConfig.DEBUGGING
lock = threading.Lock()

fileName = os.path.basename(__file__)

API_LOGGER = "http://127.0.0.1:5081"

# With static_url_path Flask serves all assets under the /static
# with no further configuration.
app = Flask(__name__)
listen_to_ip = '127.0.0.1'
listen_to_port = 5080

from webUtils import logger

fileName = os.path.basename(__file__)
lock = threading.Lock()

GPIO_SETUP = False


def logger(msg):
    if type(msg) == str and len(msg) > 0:
        payload = dict(log_entry=msg, source=fileName)
        resp = requests.post (API_LOGGER + "/new", timeout=2, data=payload)
        return resp.status_code == 200
    return False

# Shutdown and cleanup, then register the function right below.
def shutdown(*args):
    global GPIO_SETUP
    logger("GPIO shutdown() called with: " + ', '.join(args))
    with lock:
        if GPIO_SETUP:
            logger("Cleaning up GPIO.")
            GPIO.cleanup()
            logger("GPIO cleaned up.")
            GPIO_SETUP=False
        else:
            logger("GPIO cleaning not done since GPIO_SETUP is false.")

atexit.register(shutdown)
signal.signal(signal.SIGINT, lambda s, f: exit(0))
signal.signal(signal.SIGTERM, lambda s, f: exit(0))

def setup(initializer):
    global GPIO_SETUP
    if GPIO_SETUP:  # Check if already set up
        logger("Init already done, skipping from " + initializer)
        return True

    logger("Setting up GPIO Pins. Init requested from " + initializer)

    # Use BOARD mode. The pin numbers refer to the **BOARD** connector not the chip.
    # @see https://pinout.xyz/pinout/3v3_power# and the smaller numbers next to the PINs
    # in the graph
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setwarnings(True)

    # Set up the PINs as an input with a pull-up resistor.
    # These will monitor door state.
    GPIO.setup(controllerConfig.SWITCH_UPPER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(controllerConfig.SWITCH_LOWER, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Setup OPEN & CLOSE relay control. The output
    # must be set right after in order to the relay not
    # be set with a wrong value (LOW).
    GPIO.setup(controllerConfig.PINS_BUTTON_OPEN, GPIO.OUT)
    GPIO.output(controllerConfig.PINS_BUTTON_OPEN, GPIO.HIGH)
    if controllerConfig.PINS_BUTTON_OPEN != controllerConfig.PINS_BUTTON_CLOSE:
        GPIO.setup(controllerConfig.PINS_BUTTON_CLOSE, GPIO.OUT)
        GPIO.output(controllerConfig.PINS_BUTTON_OPEN, GPIO.HIGH)

    GPIO_SETUP=True
    logger("Setting up GPIO Pins ... done!")


# This triggers the Opening/Closing the door.
@app.route('/close', methods=['GET'])
def close():
    msg = "Garage door close route called "
    if controllerConfig.DRY_RUN:
        msg = "** DRY RUN ONLY ** " + msg
    logger(msg)
    with lock:
        msg = "Toggling RasPi pins @ " + datetime.datetime.now().strftime("%X")
        if controllerConfig.DRY_RUN:
            msg = "** DRY RUN ONLY ** " + msg
        GPIO.output(controllerConfig.PINS_BUTTON_CLOSE, GPIO.LOW)
        msg = "Toggling RasPi pins [" + GPIO.input(controllerConfig.PINS_BUTTON_CLOSE) + "] @ " + datetime.datetime.now().strftime("%X")
        time.sleep(.5)
        GPIO.output(controllerConfig.PINS_BUTTON_CLOSE, GPIO.HIGH)
        msg = "Toggling RasPi pins [" + GPIO.input(controllerConfig.PINS_BUTTON_CLOSE) + "] @ " + datetime.datetime.now().strftime("%X")
        return jsonify({'message': 'success'}), 200


# This triggers the Opening/Closing the door.
@app.route('/open', methods=['GET'])
def open():
    with lock:
        msg = "Garage door opening triggered "
        if controllerConfig.DRY_RUN:
            msg = "** DRY RUN ONLY ** " + msg
        logger(msg)
        GPIO.output(controllerConfig.PINS_BUTTON_OPEN, GPIO.LOW)
        time.sleep(.5)
        GPIO.output(controllerConfig.PINS_BUTTON_OPEN, GPIO.HIGH)
        return jsonify({'message': 'success'}), 200


# Read door status from magnetic switches connected to GPIO
@app.route('/status', methods=['GET'])
def status():
    # threading lock to avoid writing to log file at the same time.
    with lock:
        if GPIO.input(controllerConfig.SWITCH_LOWER) == GPIO.HIGH and GPIO.input(controllerConfig.SWITCH_UPPER) == GPIO.HIGH:
            if controllerConfig.LogLevel >= 1:
                logger("Garage is Opening/Closing")
            return jsonify({"door": f"{controllerConfig.STATE_BETWEEN}"}), 200

        else:
            if GPIO.input(controllerConfig.SWITCH_LOWER) == GPIO.LOW:
                if controllerConfig.LogLevel >= 2:
                    logger("Garage is Closed")
                return jsonify({"door": f"{controllerConfig.STATE_DOWN}"}), 200

            if GPIO.input(controllerConfig.SWITCH_UPPER) == GPIO.LOW:
                if controllerConfig.LogLevel >= 1:
                    logger("Door is Open")
                return jsonify({"door": f"{controllerConfig.STATE_UP}"}), 200
        return jsonify({"door": "?"}), 523


if __name__ == '__main__':
    try:
        msg = f'Hello from {fileName} '
        msg = msg + "(debug: " + str(debug) + ")!"
        logger(msg)
        setup(fileName)
        app.run(host=listen_to_ip, port=listen_to_port, debug=debug )
    finally:
        shutdown(json.dumps({"from": "flask.exit"}))
