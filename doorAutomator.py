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
        if debug:
            logger("Automator status() received status from Controller API: " + resp.json().get('door', 'n/a'))

        return resp.json().get("door", '')
    except Exception as e:
        logger("Automator status() received from Controller API: " + str(e))
        return None

def close():
    try:
        resp = requests.get(API_CONTROLLER + "/close", timeout=2)
        if debug:
            logger("Automator close() received status from Controller API: " + resp.json().get('door', 'n/a'))

        return resp.json().get("door", '')
    except Exception as e:
        logger("Automator close() received from Controller API: " + str(e))
        return None

def toggle():
    return close()

# Calculate time left compared to the provided value. Optional format, m for mimutes.
def timeLeft(startTime, format = 's'):
    currentTimeDate = datetime.datetime.now()
    diff = (currentTimeDate - startTime).total_seconds()
    if format = 's':
        return diff
    if format = 'm':
        return math.floor(diff)

# Read door status from magnetic switches connected to GPIO
def doorMonitor():

    DoorOpenTimerMessageSent = 1  # Turn off messages until timer is started
    logger("Door automator is starting (debug: )" + str(debug) + ")." )

    # TimeDoorOpened also implies the door is opened (fully) wnen value is not None.
    TimeDoorOpened = None
    while True:
        # Start the timer if door is open at the boot time.
        if status() == STATE_UP:  # Door is Open
            if TimeDoorOpened is None:
                TimeDoorOpened = datetime.datetime.now()
            logger("Door is open and timer is running (started " + str(TimeDoorOpened.strftime("%x %X")) + ".")
        else:
            if debug:
                logger("Door is closed.")
            TimeDoorOpened = None
        time.sleep(5)
            # Door Open Timer has Started
        if TimeDoorOpened is not None:
            logger("Door timer is ON with delay of " +
                str(math.floor(DoorOpenMessageDelay/60)) + " minutes. Door is " + status() + ".")

            currentTimeDate = datetime.datetime.now()

            if timeLeft(TimeDoorOpened) > DoorOpenMessageDelay and DoorOpenTimerMessageSent == 0:
                logger("Your Garage Door has been Open for " +
                    str(math.floor(DoorAutoCloseDelay/60)) + " minutes")
                DoorOpenTimerMessageSent = 1

            if timeLeft(TimeDoorOpened) > DoorAutoCloseDelay and DoorOpenTimerMessageSent == 1:
                logger("Closing Garage Door automatically now since it has been left Open for  " +
                    str(timeLeft(TimeDoorOpened, 'min')) + " minutes")
                close()

        # Door Status is Unknown
        if status() == STATE_BETWEEN:
            logger("Door Opening/Closing")
            while status() == STATE_BETWEEN:
                time.sleep(10)

            else:
                if status() == STATE_DOWN:
                    logger("Door Closed")

                elif status() == STATE_UP:
                    # Start Door Open Timer
                    TimeDoorOpened = datetime.datetime.now()
                    logger("Door opened fully: " +
                        str(TimeDoorOpened))
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
