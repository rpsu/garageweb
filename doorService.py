import os, math, time, threading, json
from flask import Flask


import config
from utils import logger, timeNow
import doorControls

fileName = os.path.basename(__file__)
lock = threading.Lock()

print("Starting service as a REST API")
print("Control + C to exit Program")
logger('Hello from Door servide!', fileName)

app = Flask(__name__)

# Read door status from magnetic switches connected to GPIO
def doorMonitor():

    DoorOpenTimer = 0  # Default start status turns timer off
    DoorOpenTimerMessageSent = 1  # Turn off messages until timer is started

    while True:
        with lock:
            TimeDoorOpened = timeNow()
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

                currentTimeDate = timeNow()

                if (currentTimeDate - TimeDoorOpened).seconds > config.DoorOpenMessageDelay and DoorOpenTimerMessageSent == 0:
                    logger("Your Garage Door has been Open for " +
                        str(math.floor(config.DoorOpenMessageDelay/60)) + " minutes", fileName)
                    DoorOpenTimerMessageSent = 1

                if (currentTimeDate - TimeDoorOpened).seconds > config.DoorAutoCloseDelay and DoorOpenTimerMessageSent == 1:
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
                        TimeDoorOpened = timeNow()
                        logger("Door opened fully: " +
                            str(TimeDoorOpened), fileName)
                        DoorOpenTimer = 1
                        DoorOpenTimerMessageSent = 0

@app.route("/toggle", methods=["POST"])
def toggle():
    with lock:
        # This triggers the Opening/Closing the door.
        status = doorControls.status()
        if status == config.STATE_UP:
            doorControls.close(fileName)
        elif status == config.STATE_DOWN:
            doorControls.open(fileName)
        elif status == config.STATE_BETWEEN:
            doorControls.close(fileName)

        return json.dumps({"status": doorControls.status()})


@app.route("/status", methods=["GET"])
def status():
    with lock:
        return json.dumps({"status": doorControls.status()})

if __name__ == "__main__":
    try:
        doorControls.setup(fileName)
        thread = threading.Thread(target=doorMonitor)
        thread.daemon = True  # Make this thread a daemon
        thread.start()
        app.run(host="127.0.0.1", port=8088, debug=False)
    finally:
        doorControls.shutdown()
