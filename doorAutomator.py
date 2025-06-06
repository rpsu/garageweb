import  math, time, os.path, datetime
import requests

fileName = os.path.basename(__file__)
API_CONTROLLER = "http://127.0.0.1:5080"
API_LOGGER = "http://127.0.0.1:5081"

# Door state constants.
STATE_UP = 'up'
STATE_DOWN = 'down'
STATE_BETWEEN = 'between'

debug=True

# Close door automatically after seconds (if left fully opened)
# DoorAutoCloseDelay = 1200
DoorAutoCloseDelay = 30
# Door left open message after seconds (if left fully opened)
DoorOpenMessageDelay = 300

def logger(msg):
    if type(msg) == str and len(msg) > 0:
        payload = dict(log_entry=msg, source=fileName)
        resp = requests.post(API_LOGGER + "/new", timeout=2, data=payload)
        return resp.status_code == 200
    return False

def status():
    try:
        resp = requests.get(API_CONTROLLER + "/status", timeout=2)
        return resp.json().get("door", '')
    except Exception as e:
        logger("Automator status() received from Controller API: " + str(e))
        return None

def open():
    try:
        resp = requests.get(API_CONTROLLER + "/open", timeout=2)
        return resp.json().get("door", '')
    except Exception as e:
        logger("Automator open() received from Controller API: " + str(e))
        return None

def close():
    try:
        resp = requests.get(API_CONTROLLER + "/close", timeout=2)
        return resp.json().get("door", '')
    except Exception as e:
        logger("Automator close() received from Controller API: " + str(e))
        return None

def toggle():
    return close()


# Read door status from magnetic switches connected to GPIO
def doorMonitor():

    DoorOpenTimer = 0  # Default start status turns timer off
    DoorOpenTimerMessageSent = 1  # Turn off messages until timer is started
    logger("Door automator is starting (debug: )" + str(debug) + ")." )

    while True:
        TimeDoorOpened = datetime.datetime.now()
        # Start the timer if door is open at the boot time.
        if status() == STATE_UP:  # Door is Open
            logger("Door is open and timer is running (started " + str(TimeDoorOpened) + ".")
            DoorOpenTimer = 1
        else:
            if debug:
                logger("Door is closed.")
            DoorOpenTimer = 0
        time.sleep(5)
            # Door Open Timer has Started
        if DoorOpenTimer == 1:
            logger("Door timer is ON with delay of " +
                str(math.floor(DoorOpenMessageDelay/60)) + " minutes. Door is " + status() + ".")

            currentTimeDate = datetime.datetime.now()

            if (currentTimeDate - TimeDoorOpened).total_seconds() > DoorOpenMessageDelay and DoorOpenTimerMessageSent == 0:
                logger("Your Garage Door has been Open for " +
                    str(math.floor(DoorOpenMessageDelay/60)) + " minutes")
                DoorOpenTimerMessageSent = 1

            if (currentTimeDate - TimeDoorOpened).total_seconds() > DoorAutoCloseDelay and DoorOpenTimerMessageSent == 1:
                logger("Closing Garage Door automatically now since it has been left Open for  " +
                    str(math.floor(DoorAutoCloseDelay/60)) + " minutes")
                close(fileName)
                DoorOpenTimer = 0

        # Door Status is Unknown
        if status() == STATE_BETWEEN:
            logger("Door Opening/Closing")
            while status() == STATE_BETWEEN:
                time.sleep(10)

            else:
                if status() == STATE_DOWN:
                    logger("Door Closed")
                    DoorOpenTimer = 0

                elif status() == STATE_UP:
                    # Start Door Open Timer
                    TimeDoorOpened = datetime.datetime.now()
                    logger("Door opened fully: " +
                        str(TimeDoorOpened))
                    DoorOpenTimer = 1
                    DoorOpenTimerMessageSent = 0

if __name__ == '__main__':
    try:
        msg = f'Hello from {fileName} '
        msg = msg + "(debug: " + str(debug) + ")!"
        logger(msg)
        doorMonitor()
    finally:
        msg = f'Door Automator is shut down {fileName} '
        msg = msg + "(debug: " + str(debug) + ")!"
        logger(msg)
