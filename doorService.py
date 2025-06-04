import os, math, time, threading, json, datetime, logging
from flask import Flask

import config
from utils import logger
import doorControls

fileName = os.path.basename(__file__)
lock = threading.Lock()

print("Starting service as a REST API")
print("Control + C to exit Program")
logger('Hello from Door servide!', fileName)

app = Flask(__name__)

# Configure Flask logging mainly for the UTF-8 filesystem.
logging.basicConfig(
    format='%(asctime)s %(levelname)s [%(module)s] %(message)s',
    level=logging.INFO,
    datefmt='%a, %d %b %Y %H:%M:%S',
    encoding='utf-8'
)
if config.DEBUGGING:
    logging.basicConfig(level=logging.DEBUG)


# Read door status from magnetic switches connected to GPIO
def doorMonitor():

    DoorOpenTimer = 0  # Default start status turns timer off
    DoorOpenTimerMessageSent = 1  # Turn off messages until timer is started

    while True:
        with lock:
            TimeDoorOpened = datetime.datetime.now()
            # Start the timer if door is open at the boot time.
            if doorControls.status() == config.STATE_UP:  # Door is Open
                logger("Door is Open and timer is running.", fileName)
                DoorOpenTimer = 1
            else:
                DoorOpenTimer = 0
            time.sleep(5)
             # Door Open Timer has Started
            if DoorOpenTimer == 1:
                logger("Door timer is ON with delay of " +
                    str(math.floor(config.DoorOpenMessageDelay/60)) + " minutes. Door is " + doorControls.status() + ".", fileName)

                currentTimeDate = datetime.datetime.now()

                if (currentTimeDate - TimeDoorOpened).total_seconds() > config.DoorOpenMessageDelay and DoorOpenTimerMessageSent == 0:
                    logger("Your Garage Door has been Open for " +
                        str(math.floor(config.DoorOpenMessageDelay/60)) + " minutes", fileName)
                    DoorOpenTimerMessageSent = 1

                if (currentTimeDate - TimeDoorOpened).total_seconds() > config.DoorAutoCloseDelay and DoorOpenTimerMessageSent == 1:
                    logger("Closing Garage Door automatically now since it has been left Open for  " +
                        str(math.floor(config.DoorAutoCloseDelay/60)) + " minutes", fileName)
                    doorControls.close(fileName)
                    DoorOpenTimer = 0

            # Door Status is Unknown
            if doorControls.status() == config.STATE_BETWEEN:
                logger("Door Opening/Closing", fileName)
                while doorControls.status() == config.STATE_BETWEEN:
                    time.sleep(10)

                else:
                    if doorControls.status() == config.STATE_DOWN:
                        logger("Door Closed", fileName)
                        DoorOpenTimer = 0

                    elif doorControls.status() == config.STATE_UP:
                        # Start Door Open Timer
                        TimeDoorOpened = datetime.datetime.now()
                        logger("Door opened fully: " +
                            str(TimeDoorOpened), fileName)
                        DoorOpenTimer = 1
                        DoorOpenTimerMessageSent = 0

@app.route("/toggle", methods=["POST"])
def toggle():
    # This triggers the Opening/Closing the door.
    status = doorControls.status()
    if status == config.STATE_UP:
        doorControls.close(fileName)
    elif status == config.STATE_DOWN:
        doorControls.open(fileName)
    elif status == config.STATE_BETWEEN:
        doorControls.close(fileName)
    time.sleep(0.5)
    return json.dumps({"status": doorControls.status()})


@app.route("/status", methods=["GET"])
def status():
    try:
        status = doorControls.status()
        return json.dumps({"status": status})
    finally:
        return json.dumps({"error": "status not received", "code": 501})

if __name__ == "__main__":
    try:
        doorControls.setup(fileName)
        thread = threading.Thread(target=doorMonitor)
        thread.daemon = True  # Make this thread a daemon
        thread.start()
        app.run(host="127.0.0.1", port=8088, debug={config.DEBUGGING})
    finally:
        doorControls.shutdown()
