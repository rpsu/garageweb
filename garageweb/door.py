import time
import config
import os.path
from utils import logger
import platform
import traceback
import mock
from gpiozero import OutputDevice, InputDevice
from unittest.mock import MagicMock

# global initialized, raspi
raspi = False
initialized = False
fileName = os.path.basename(__file__)

print("Door code seems to run on: '" + platform.machine() + "'")

if platform.machine() == 'armv7l':
    raspi = True
    logger("Door code seems to run on Raspi.", fileName, 2)
    # We are not on macOS
else:
    logger("Door code seems to run on MacOS.", fileName, 2)
    # We are on macOS
    OutputDevice = mock.MagicMock()
    InputDevice = mock.MagicMock()


doorClose = None
doorOpen = None
upperEye = None
lowerEye = None

def setup(initializer):
    """
    Initializes the door object.

    Args:
        initializer: The source of the initialization request.

    Returns:
        None
    """
    global doorClose, doorOpen, upperEye, lowerEye, initialized, raspi
    if initialized:
        logger("setup() was already done. Request from " + initializer, fileName, 2)
        return

    initialized = True
    logger("Setting up PINs. Request from " + initializer, fileName, 1)
    if raspi:
        # doorClose.on() + doorClose.off() (with short pause)
        # triggers the Opening/Closing the door.
        # @see gpiozero docs https://gpiozero.readthedocs.io/
        doorClose = OutputDevice(config.PINS_BUTTON_CLOSE)
        doorOpen = OutputDevice(config.PINS_BUTTON_OPEN)

        # Magnetic switch *closes* (= value 0) when magnets meet each other.
        # Example: When door is up, upperEye value is 0.
        upperEye = InputDevice(config.SWITCH_UPPER)
        lowerEye = InputDevice(config.SWITCH_LOWER)

        # Use BOARD mode. The pin numbers refer to the **BOARD** connector not the chip.
        # @see https://pinout.xyz/pinout/3v3_power# and the smaller numbers next to the PINs
        # in the graph
        # Set up the PINs as an input with a pull-up resistor.
        # These will monitor door state.

        # # Setup OPEN & CLOSE relay control. The output
        # # must be set right after in order to the relay not
        # # be set with a wrong value (LOW).
        # GPIO.setup(config.PINS_BUTTON_OPEN, GPIO.OUT)
        # GPIO.output(config.PINS_BUTTON_OPEN, GPIO.HIGH)
        # if config.PINS_BUTTON_OPEN != config.PINS_BUTTON_CLOSE:
        #     GPIO.setup(config.PINS_BUTTON_CLOSE, GPIO.OUT)
        #     GPIO.output(config.PINS_BUTTON_OPEN, GPIO.HIGH)
    else:
        logger("Setting up GPIO Pins with MagicMock... done!", fileName, 1)
        doorClose = MagicMock()
        doorOpen = MagicMock()

        # Read door status from magnetic switches connected to GPIO
        upperEye = MagicMock()
        upperEye.is_active = mock.MagicMock()
        upperEye.value.return_value = 1
        lowerEye = MagicMock()
        lowerEye.is_active = mock.MagicMock()
        lowerEye.value.return_value = 0

    logger("Setting up GPIO Pins ... done!", fileName, 1)

    return

# This triggers the Opening/Closing the door.
def closeTheDoor(fromFile):
    logger("Garage door closing triggered by " + fromFile, fileName, 1)
    doorClose.on()
    time.sleep(.5)
    doorClose.off()


# This triggers the Opening/Closing the door.
def openTheDoor(fromFile):
    logger("Garage door opening triggered by " + fromFile, fileName)
    doorOpen.on()
    time.sleep(.5)
    doorOpen.off()



def getTheDoorStatus():
    stack_trace = traceback.format_stack()
    logger("Status function called from: " + ''.join(stack_trace), fileName, 3)

    global upperEye, lowerEye

    lower = lowerEye.value()
    upper = upperEye.value()
    logger("Garage door eyes are: upper " + str(upper) , fileName, 2)
    logger("Garage door eyes are: lower " + str(lower) , fileName, 2)
    if lower == 1  and upper == 1:
        logger("Garage door is in between state (or moving)", fileName, 1)
        return config.STATE_BETWEEN

    if lower == 1  and upper == 0:
        logger("Door is Open", fileName, 1)
        return config.STATE_UP
    if lower == 0  and upper == 1:
        logger("Door is Closed", fileName, 1)
        return config.STATE_DOWN

    if lower == 0  and upper == 0:
        logger("Door monitoring is BROKEN, both switches are closed", fileName, 0)
        return

def cleanup():
    global raspi, doorClose, doorOpen, upperEye, lowerEye
    logger("Cleaning up", fileName, 1)
    if raspi:
        doorClose.close()
        doorOpen.close()
        upperEye.close()
        lowerEye.close()
        logger("Raspi pins released", fileName, 1)
    else:
        logger("No cleanup needed", fileName, 1)
