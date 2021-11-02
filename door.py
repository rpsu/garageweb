import os.path
import RPi.GPIO as GPIO
import time
import math
import os.path
from datetime import datetime
# Custom modules
import utils
import config

fileName = os.path.basename(__file__)

print("Control + C to exit Program")

utils.logger('Hello from Door Monitoring!', fileName)
utils.logger("Setting up GPIO Pins", fileName)

# Use BOARD mode. The pin numbers refer to the **BOARD** connector not the chip.
# @see https://pinout.xyz/pinout/3v3_power# and the smaller numbers next to the PINs
# in the graph
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

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

utils.logger("Setting up GPIO Pins ... done!", fileName)

TimeDoorOpened = datetime.strptime(datetime.strftime(
    datetime.now(), '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')  # Default Time

DoorOpenTimer = 0  # Default start status turns timer off
DoorOpenTimerMessageSent = 1  # Turn off messages until timer is started
# Close door automatically after seconds (if left fully opened)
DoorAutoCloseDelay = 1200
# Door left open message after seconds (if left fully opened)
DoorOpenMessageDelay = 900


# Start the timer if door is open at the boot time.
if utils.door_status() == 'opened':
    utils.logger(
        "Door is Open when booting up. Turn Door opened timer initally on.", fileName)
    # Start Door Open Timer
    DoorOpenTimer = 1


# Read door status from magnetic switches connected to GPIO
try:
    while 1 >= 0:
        time.sleep(1)
        state = utils.door_status()
        if DoorOpenTimer == 1:  # Door Open Timer has Started
            currentTimeDate = datetime.strptime(datetime.strftime(
                datetime.now(), '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
            if (currentTimeDate - TimeDoorOpened).seconds > DoorOpenMessageDelay and DoorOpenTimerMessageSent == 0:
                utils.logger("Your Garage Door has been Open for " +
                             str(math.floor(DoorOpenMessageDelay/60)) + " minutes", fileName)
                DoorOpenTimerMessageSent = 1

            if (currentTimeDate - TimeDoorOpened).seconds > DoorAutoCloseDelay and DoorOpenTimerMessageSent == 1:
                utils.logger("Closing Garage Door automatically, since it has been left Open for  " +
                             str(math.floor(DoorAutoCloseDelay/60)) + " minutes", fileName)
                time.sleep(2)
                # This triggers the Opening/Closing the door.
                GPIO.output(config.PINS_BUTTON_CLOSE, GPIO.LOW)
                time.sleep(.5)
                GPIO.output(config.PINS_BUTTON_CLOSE, GPIO.HIGH)

        # Door Status is Unknown
        if state == 'in-between':
            utils.logger("Door Opening/Closing", fileName)
            while state == 'in-between':
                # Door is not closed nor open.
                time.sleep(.5)
                state = utils.door_status()
            else:
                if state == 'closed':
                    utils.logger("Door Closed", fileName)
                    DoorOpenTimer = 0

                elif state == 'opened':
                    utils.logger("Door Open", fileName)
                    # Start Door Open Timer
                    TimeDoorOpened = datetime.strptime(datetime.strftime(
                        datetime.now(), '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                    utils.logger("Door opened fully: " +
                                 str(TimeDoorOpened), fileName)
                    DoorOpenTimer = 1
                    DoorOpenTimerMessageSent = 0


except KeyboardInterrupt:
    utils.logger("Monitoring is shut down -- Goodbye!", fileName)
    GPIO.cleanup()
