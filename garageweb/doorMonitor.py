import os
import time
import math
import os.path
from datetime import datetime
import config
from utils import logger
import door

print("Control + C to exit Program")

fileName = os.path.basename(__file__)

logger('Hello from Door Monitoring!', fileName)
door.setup(fileName)

TimeDoorOpened = datetime.strptime(datetime.strftime(
    datetime.now(), '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')  # Default Time

DoorOpenTimer = 0  # Default start status turns timer off
DoorOpenTimerMessageSent = 1  # Turn off messages until timer is started


# Start the timer if door is open at the boot time.
if door.getTheDoorStatus() == config.STATE_UP:  # Door is Open
    logger("Door is Open when starting the door monitoring. Turn the 'Door is opened' timer initally on.", fileName)
    DoorOpenTimer = 1
else:
    logger("Door is '" + door.getTheDoorStatus() +
           "' when starting the door monitoring. ", fileName)
    DoorOpenTimer = 0

def run():
    global TimeDoorOpened, DoorOpenTimer, DoorOpenTimerMessageSent
    logger("Door Monitoring is started", fileName, 2)
    # Read door status from magnetic switches connected to GPIO
    try:
        while 1 >= 0:
            time.sleep(5)
            state = door.getTheDoorStatus()
            if DoorOpenTimer == 1:  # Door Open Timer has Started
                logger("Door timer is ON with delay of " +
                    str(math.floor(config.DoorOpenMessageDelay/60)) + " minutes. Door is " + state + ".", fileName)

                currentTimeDate = datetime.strptime(datetime.strftime(
                    datetime.now(), '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')

                if (currentTimeDate - TimeDoorOpened).seconds > config.DoorOpenMessageDelay and DoorOpenTimerMessageSent == 0:
                    logger("Your Garage Door has been Open for " +
                        str(math.floor(config.DoorOpenMessageDelay/60)) + " minutes", fileName)
                    DoorOpenTimerMessageSent = 1

                if (currentTimeDate - TimeDoorOpened).seconds > config.DoorAutoCloseDelay and DoorOpenTimerMessageSent == 1:
                    logger("Closing Garage Door automatically now since it has been left Open for  " +
                        str(math.floor(config.DoorAutoCloseDelay/60)) + " minutes", fileName)
                    door.closeTheDoor(fileName)
                    DoorOpenTimer = 0

            # Door Status is Unknown
            if state == config.STATE_BETWEEN:
                logger("Door Opening/Closing", fileName)
                while state == config.STATE_BETWEEN:
                    # Door is not closed nor open.
                    time.sleep(5)
                    state = door.getTheDoorStatus()
                else:
                    if state == config.STATE_DOWN:
                        logger("Door Closed", fileName)
                        DoorOpenTimer = 0

                    elif state == config.STATE_UP:
                        logger("Door Open", fileName)
                        # Start Door Open Timer
                        TimeDoorOpened = datetime.strptime(datetime.strftime(
                            datetime.now(), '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                        logger("Door opened fully: " +
                            str(TimeDoorOpened), fileName)
                        DoorOpenTimer = 1
                        DoorOpenTimerMessageSent = 0

        logger("Door Monitoring is ending", fileName, 2)

    except KeyboardInterrupt:
        logger("Monitoring is shut down -- Goodbye!", fileName, 1)
        door.cleanup()
    except Exception as e:
        logger("An error occurred: " + str(e), fileName, 0)
        door.cleanup()
