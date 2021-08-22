import os
import RPi.GPIO as GPIO
import time
import math
import os.path

from datetime import datetime

VerboseConsole = False  # Wether or not print messages to console as well.

fileName = os.path.basename(__file__)

# Define which GPIO pins do what.
# Open and close may be the same or different.
PINS_BUTTON_OPEN = 11
PINS_BUTTON_CLOSE = 11
# Upper magnetic switch *closes* (value 0) when door is open.
SWITCH_UPPER = 18
# Upper magnetic switch *closes* (value 0) when door is closed.
SWITCH_LOWER = 16


def logger(msg):
    logfile = open("/home/pi/GarageWeb/static/log.txt", "a")
    logfile.write(datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S [" + fileName + "] -- " + msg + "\n"))
    logfile.close()
    if VerboseConsole == True:
        print(msg)


logger('Hello from monitoring!')

print("Control + C to exit Program")


logger("Setting up GPIO Pins")

# Use BOARD mode. The pin numbers refer to the **BOARD** connector not the chip.
# @see https://pinout.xyz/pinout/3v3_power# and the smaller numbers next to the PINs
# in the graph
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Set up the PINs as an input with a pull-up resistor.
# These will monitor door state.
GPIO.setup(SWITCH_UPPER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SWITCH_LOWER, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Specify an initial value for your output channel.
GPIO.setup(PINS_BUTTON_OPEN, GPIO.OUT)
if PINS_BUTTON_OPEN != PINS_BUTTON_CLOSE:
    GPIO.setup(PINS_BUTTON_CLOSE, GPIO.OUT)

logger("Setting up GPIO Pins ... done!")
time.sleep(1)
logger("Checking the initial state!")
state = 'not' if GPIO.input(SWITCH_UPPER) == GPIO.LOW else ''
logger('"Door Open" switch is ' + state + ' closed.')
state = 'not' if GPIO.input(SWITCH_LOWER) == GPIO.LOW else ''
logger('"Door Closed" switch is ' + state + ' closed.')


TimeDoorOpened = datetime.strptime(datetime.strftime(
    datetime.now(), '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')  # Default Time

DoorOpenTimer = 0  # Default start status turns timer off
DoorOpenTimerMessageSent = 1  # Turn off messages until timer is started
# Close door automatically after seconds (if left fully opened)
DoorAutoCloseDelay = 1200
# Door left open message after seconds (if left fully opened)
DoorOpenMessageDelay = 900

# Start the timer if door is open at the boot time.
if GPIO.input(SWITCH_UPPER) == GPIO.LOW:  # Door is Open
    logger("Door is Open on bootup.")
    # Start Door Open Timer
    DoorOpenTimer = 1


try:
    while 1 >= 0:
        time.sleep(1)
        if DoorOpenTimer == 1:  # Door Open Timer has Started
            currentTimeDate = datetime.strptime(datetime.strftime(
                datetime.now(), '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
            if (currentTimeDate - TimeDoorOpened).seconds > DoorOpenMessageDelay and DoorOpenTimerMessageSent == 0:
                logger("Your Garage Door has been Open for " +
                       str(math.floor(DoorOpenMessageDelay/60)) + " minutes")
                DoorOpenTimerMessageSent = 1

            if (currentTimeDate - TimeDoorOpened).seconds > DoorAutoCloseDelay and DoorOpenTimerMessageSent == 1:
                logger("Closing Garage Door automatically, since it has been left Open  " +
                       str(math.floor(DoorAutoCloseDelay/60)) + " minutes")
                time.sleep(2)
                # This triggers the Opening/Closing the door.
                GPIO.output(PINS_BUTTON_CLOSE, GPIO.LOW)
                time.sleep(.5)
                GPIO.output(PINS_BUTTON_CLOSE, GPIO.HIGH)

        # Door Status is Unknown
        if GPIO.input(SWITCH_LOWER) == GPIO.HIGH and GPIO.input(SWITCH_UPPER) == GPIO.HIGH:
            logger("Door Opening/Closing")
            while GPIO.input(SWITCH_LOWER) == GPIO.HIGH and GPIO.input(SWITCH_UPPER) == GPIO.HIGH:
                # Door is not closed nor open.
                time.sleep(.5)
            else:
                if GPIO.input(SWITCH_LOWER) == GPIO.LOW:  # Door is Closed
                    logger("Door Closed")
                    DoorOpenTimer = 0

                if GPIO.input(SWITCH_UPPER) == GPIO.LOW:  # Door is Open
                    logger("Door Open")
                    # Start Door Open Timer
                    TimeDoorOpened = datetime.strptime(datetime.strftime(
                        datetime.now(), '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                    logger("Door opened fully: " + str(TimeDoorOpened))
                    DoorOpenTimer = 1
                    DoorOpenTimerMessageSent = 0


except KeyboardInterrupt:
    logger("Monitoring is shut down -- Goodbye!")
    GPIO.cleanup()
