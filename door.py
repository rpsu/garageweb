import os
import RPi.GPIO as GPIO
import time
from datetime import datetime

VerboseConsole = False  # Wether or not print messages to console as well.


def logger(msg):
    logfile = open("/home/pi/GarageWeb/static/log.txt", "a")
    logfile.write(datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S [log.py] -- " + msg + "\n"))
    logfile.close()
    if VerboseConsole == True:
        print(msg)


logger('Hello!')

print " Control + C to exit Program"


logger("Setting up GPIO Pins")
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
logger("Setting up GPIO Pins ... done!")
time.sleep(1)

TimeDoorOpened = datetime.strptime(datetime.strftime(
    datetime.now(), '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')  # Default Time

DoorOpenTimer = 0  # Default start status turns timer off
DoorOpenTimerMessageSent = 1  # Turn off messages until timer is started
# Close door automatically after seconds (if left fully opened)
DoorAutoCloseDelay = 120
# Door left open message after seconds (if left fully opened)
DoorOpenMessageDelay = 60

try:
    while 1 >= 0:
        time.sleep(1)
        if DoorOpenTimer == 1:  # Door Open Timer has Started
            currentTimeDate = datetime.strptime(datetime.strftime(
                datetime.now(), '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
            if (currentTimeDate - TimeDoorOpened).seconds > DoorOpenMessageDelay and DoorOpenTimerMessageSent == 0:
                logger("Your Garage Door has been Open for " +
                       str(DoorOpenMessageDelay/60) + " minutes")
                DoorOpenTimerMessageSent = 1

            if (currentTimeDate - TimeDoorOpened).seconds > DoorAutoCloseDelay and DoorOpenTimerMessageSent == 0:
                logger("Closing Garage Door automatically, since it has been left Open  " +
                       str(DoorAutoCloseDelay/60) + " minutes")
                time.sleep(5)
                logger("Setting Pin 11 to " + str(GPIO.HIGH))
                GPIO.output(11, GPIO.HIGH)
                time.sleep(2)
                logger("Setting Pin 11 to " + str(GPIO.LOW))
                GPIO.output(11, GPIO.LOW)
                time.sleep(2)
                logger("Setting Pin 11 to " + str(GPIO.HIGH))
                GPIO.output(11, GPIO.HIGH)
                time.sleep(5)

        if GPIO.input(16) == GPIO.HIGH and GPIO.input(18) == GPIO.HIGH:  # Door Status is Unknown
            logger("Door Opening/Closing")
            while GPIO.input(16) == GPIO.HIGH and GPIO.input(18) == GPIO.HIGH:
                time.sleep(.5)
            else:
                if GPIO.input(16) == GPIO.LOW:  # Door is Closed
                    logger("Door Closed")
                    DoorOpenTimer = 0

                if GPIO.input(18) == GPIO.LOW:  # Door is Open
                    logger("Door Open")
                    # Start Door Open Timer
                    TimeDoorOpened = datetime.strptime(datetime.strftime(
                        datetime.now(), '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                    DoorOpenTimer = 1
                    DoorOpenTimerMessageSent = 0


except KeyboardInterrupt:
    logger("Log Program Shutdown -- Goodbye!")
    GPIO.cleanup()
