import atexit, signal, time, os.path, requests, datetime, sys, traceback, re
import RPi.GPIO as GPIO
from flask import Flask, json, jsonify
from dotenv import dotenv_values

from webUtils import logger

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

API_LOGGER = "http://127.0.0.1:" + str(config.get("API_LOGGER_PORT"))

# With static_url_path Flask serves all assets under the /static
# with no further configuration.
app = Flask(__name__)
listen_to_ip = '127.0.0.1'
listen_to_port = str(config.get("API_CONTROLLER_PORT"))

GPIO_SETUP = False

def logger(msg):
    if type(msg) == str and len(msg) > 0:
        payload = dict(log_entry=msg, source=fileName)
        resp = requests.post (API_LOGGER + "/new", timeout=2, data=payload)
        return resp.status_code == 200
    return False

# Shutdown and cleanup, then register the function right below.
def shutdown(*args):
    traceback.print_exc(file=sys.stdout)
    global GPIO_SETUP
    logger("GPIO shutdown() called with: " + ', '.join(args))
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
    traceback.print_exc(file=sys.stdout)
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
    GPIO.setup(config.get("SWITCH_UPPER"), GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(config.get("SWITCH_LOWER"), GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Setup OPEN & CLOSE relay control. The output
    # must be set right after in order to the relay not
    # be set with a wrong value (LOW).
    GPIO.setup(config.get("PINS_BUTTON_OPEN"), GPIO.OUT)
    GPIO.output(config.get("PINS_BUTTON_OPEN"), GPIO.HIGH)
    if config.get("PINS_BUTTON_OPEN") != config.get("PINS_BUTTON_CLOSE"):
        GPIO.setup(config.get("PINS_BUTTON_CLOSE"), GPIO.OUT)
        GPIO.output(config.get("PINS_BUTTON_OPEN"), GPIO.HIGH)

    GPIO_SETUP=True
    logger("Setting up GPIO Pins ... done!")


# This triggers the Opening/Closing the door.
@app.route('/close', methods=['GET'])
def close():
    msg = "Garage door route /close called "
    if config.get("DRY_RUN"):
        msg = "** DRY RUN ONLY ** " + msg
    logger(msg)
    msg = "Toggling RasPi pins @ " + datetime.datetime.now().strftime("%X")
    if config.get("DRY_RUN"):
        msg = "** DRY RUN ONLY ** " + msg
    logger(msg)
    if(debug):
        logGPIOStatuses()
    GPIO.output(config.get("PINS_BUTTON_CLOSE"), GPIO.LOW)
    msg = "Toggling RasPi pins [" + str(GPIO.input(config.get("PINS_BUTTON_CLOSE"))) + "] @ " + datetime.datetime.now().strftime("%X")
    logger(msg)
    time.sleep(.5)
    if(debug):
        logGPIOStatuses()
    GPIO.output(config.get("PINS_BUTTON_CLOSE"), GPIO.HIGH)
    msg = "Toggling RasPi pins [" + str(GPIO.input(config.get("PINS_BUTTON_CLOSE"))) + "] @ " + datetime.datetime.now().strftime("%X")
    logger(msg)
    if(debug):
        logGPIOStatuses()
    return jsonify({'message': 'success'}), 200


# This triggers the Opening/Closing the door.
@app.route('/open', methods=['GET'])
def open():
    msg = "Garage door route /open called "
    if config.get("DRY_RUN"):
        msg = "** DRY RUN ONLY ** " + msg
    logger(msg)
    if(debug):
        logGPIOStatuses()
    GPIO.output(config.get("PINS_BUTTON_OPEN"), GPIO.LOW)
    time.sleep(.5)
    if(debug):
        logGPIOStatuses()
    GPIO.output(config.get("PINS_BUTTON_OPEN"), GPIO.HIGH)
    if(debug):
        logGPIOStatuses()
    return jsonify({'message': 'success'}), 200

def logGPIOStatuses():
    msg = "Statuses:: "
    msg = msg + "Button: "
    if GPIO.input(config.get("PINS_BUTTON_OPEN")) == GPIO.HIGH:
      msg = msg + " down/pressed"
    else:
      msg = msg + " up/unpressed"
    msg = ". Switches: "
    if GPIO.input(config.get("SWITCH_LOWER")) == GPIO.HIGH:
      msg = msg + " lower is open"
    else:
      msg = msg + " lower is closed"
    if GPIO.input(config.get("SWITCH_UPPER")) == GPIO.HIGH:
      msg = msg + " upper is open"
    else:
      msg = msg + " upper is closed"
    logger(msg)

# Read door status from magnetic switches connected to GPIO
@app.route('/status', methods=['GET'])
def status():
    if GPIO.input(config.get("SWITCH_LOWER")) == GPIO.HIGH and GPIO.input(config.get("SWITCH_UPPER")) == GPIO.HIGH:
        if int(config.get("LogLevel")) >= 1:
            logger("Garage is Opening/Closing")
        return jsonify({"door": config.get("STATE_BETWEEN")}), 200

    else:
        if GPIO.input(config.get("SWITCH_LOWER")) == GPIO.LOW:
            if int(config.get("LogLevel")) >= 2:
                logger("Garage is Closed")
            return jsonify({"door": config.get("STATE_DOWN")}), 200

        if GPIO.input(config.get("SWITCH_UPPER")) == GPIO.LOW:
            if int(config.get("LogLevel")) >= 1:
                logger("Door is Open")
            return jsonify({"door": config.get("STATE_UP")}), 200
    return jsonify({"door": "?"}), 523


if __name__ == '__main__':
    try:
        msg = f'Hello from {fileName} '
        msg = msg + "(debug: " + str(debug) + ")!"
        logger(msg)
        setup(fileName)
        app.run(host=listen_to_ip, port=listen_to_port, debug="${debug}")
    finally:
        shutdown(json.dumps({"from": "flask.exit"}))
