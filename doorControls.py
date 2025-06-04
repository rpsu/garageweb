import atexit, signal, time, config, os.path, threading
import RPi.GPIO as GPIO

from utils import logger

fileName = os.path.basename(__file__)
lock = threading.Lock()

GPIO_SETUP = False

# Shutdown and cleanup, then register the function right below.
def shutdown(*args):
    logger("GPIO shutdown() called with: " + ', '.join(args), fileName)
    with lock:
        if GPIO_SETUP:
            logger("Cleaning up GPIO.", fileName)
            GPIO.cleanup()
            logger("GPIO cleaned up.", fileName)
            GPIO_SETUP=False
        else:
            logger("GPIO cleaning not done since GPIO_SETUP is false.", fileName)

atexit.register(shutdown)
signal.signal(signal.SIGINT, lambda s, f: exit(0))
signal.signal(signal.SIGTERM, lambda s, f: exit(0))

def setup(initializer):
    global GPIO_SETUP
    if GPIO_SETUP:  # Check if already set up
        logger("Init already done, skipping from " + initializer, fileName)
        return True

    logger("Setting up GPIO Pins. Init requested from " + initializer, fileName)
    # Use BOARD mode. The pin numbers refer to the **BOARD** connector not the chip.
    # @see https://pinout.xyz/pinout/3v3_power# and the smaller numbers next to the PINs
    # in the graph
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setwarnings(True)

    # Set up the PINs as an input with a pull-up resistor.
    # These will monitor door state.
    GPIO.setup(config.SWITCH_UPPER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(config.SWITCH_LOWER, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Setup OPEN & CLOSE relay control. The output
    # must be set right after in order to the relay not
    # be set with a wrong value (LOW).
    GPIO.setup(config.PINS_BUTTON_OPEN, GPIO.OUT)
    GPIO.output(config.PINS_BUTTON_OPEN, GPIO.HIGH)
    if config.PINS_BUTTON_OPEN != config.PINS_BUTTON_CLOSE:
        GPIO.setup(config.PINS_BUTTON_CLOSE, GPIO.OUT)
        GPIO.output(config.PINS_BUTTON_OPEN, GPIO.HIGH)

    GPIO_SETUP=True
    logger("Setting up GPIO Pins ... done!", fileName)


# This triggers the Opening/Closing the door.
def close(fromFile):
    with lock:
        msg = "Garage door closing triggered by " + fromFile
        if config.DRY_RUN:
            msg = "** DRY RUN ONLY ** " + msg
        logger(msg, fileName)
        GPIO.output(config.PINS_BUTTON_CLOSE, GPIO.LOW)
        time.sleep(.5)
        GPIO.output(config.PINS_BUTTON_CLOSE, GPIO.HIGH)


# This triggers the Opening/Closing the door.
def open(fromFile):
    with lock:
        msg = "Garage door opening triggered by " + fromFile
        if config.DRY_RUN:
            msg = "** DRY RUN ONLY ** " + msg
        logger(msg, fileName)
        GPIO.output(config.PINS_BUTTON_OPEN, GPIO.LOW)
        time.sleep(.5)
        GPIO.output(config.PINS_BUTTON_OPEN, GPIO.HIGH)


# Read door status from magnetic switches connected to GPIO
def status():
    # threading lock to avoid writing to log file at the same time.
    with lock:
        if GPIO.input(config.SWITCH_LOWER) == GPIO.HIGH and GPIO.input(config.SWITCH_UPPER) == GPIO.HIGH:
            if config.LogLevel >= 1:
                logger("Garage is Opening/Closing", fileName)
            return config.STATE_BETWEEN
        else:
            if GPIO.input(config.SWITCH_LOWER) == GPIO.LOW:
                if config.LogLevel >= 2:
                    logger("Garage is Closed", fileName)
                return config.STATE_DOWN

            if GPIO.input(config.SWITCH_UPPER) == GPIO.LOW:
                if config.LogLevel >= 1:
                    logger("Door is Open", fileName)
                return config.STATE_UP
