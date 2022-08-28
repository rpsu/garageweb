import RPi.GPIO as GPIO
from datetime import datetime
import time
import config
import os.path
from utils import logger

fileName = os.path.basename(__file__)

# This triggers the Opening/Closing the door.


def setup(initializer):
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

    logger("Setting up GPIO Pins ... done!", fileName)


# This triggers the Opening/Closing the door.
def close(fromFile):
    logger("Garage door closing triggered by " + fromFile, fileName)
    GPIO.output(config.PINS_BUTTON_CLOSE, GPIO.LOW)
    time.sleep(.5)
    GPIO.output(config.PINS_BUTTON_CLOSE, GPIO.HIGH)


# This triggers the Opening/Closing the door.
def open(fromFile):
    logger("Garage door opening triggered by " + fromFile, fileName)
    GPIO.output(config.PINS_BUTTON_OPEN, GPIO.LOW)
    time.sleep(.5)
    GPIO.output(config.PINS_BUTTON_OPEN, GPIO.HIGH)


# Read door status from magnetic switches connected to GPIO
def status():
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
