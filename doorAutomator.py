import  math, time, os.path, datetime
import requests
from dotenv import dotenv_values

# Load .env files
config = {
    **dotenv_values(".env.default"),  # load what came with the repo
    **dotenv_values(".env"),  # load overrides from the local
}
fileName = os.path.basename(__file__)
debug = config.get("DEBUG", True)

for k, v in config.items():
    if v == 'False':
        config.get(k) = False
    elif v == 'True':
        config.get(k) = True
if debug:
    print("Config in ${fileName}: ")
    for k, v in config.items():
        print(str(k) + " => [" + str(type(v)) + "] " + str(v))

API_CONTROLLER = "http://127.0.0.1:" + config.get("API_CONTROLLER_PORT")
API_LOGGER = "http://127.0.0.1:" + config.get("API_LOGGER_PORT")

# Door state constants.
STATE_UP = config.get("STATE_UP")
STATE_DOWN = config.get("STATE_DOWN")
STATE_BETWEEN = config.get("STATE_BETWEEN")


# Close door automatically after seconds (if left fully opened)
DoorAutoCloseDelay = 360
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
    if format == 's' or format == 'sec':
        return diff
    if format == 'm' or format == 'min':
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
            logger("Door is open and timer is running [now left " + str(DoorAutoCloseDelay - math.floor(timeLeft(TimeDoorOpened)))+ " s] (started " + str(TimeDoorOpened.strftime("%X")) + ").")
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
