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
