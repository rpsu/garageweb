import RPi.GPIO as GPIO
import time
from datetime import datetime

print("Control + C to exit Program")

# Swithces "door is up" and "door is down".
SWITCH_UPPER = 18
SWITCH_LOWER = 16


def logger(msg, fileName='??'):
    logfile = open("/home/pi/GarageWeb/static/log.txt", "a")
    logfile.write(datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S [" + fileName + "] - - " + msg + "\n"))
    logfile.close()
    print(msg)


# the pin numbers refer to the board connector not the chip
GPIO.setmode(GPIO.BOARD)
logger("Setting warnings to True")
GPIO.setwarnings(True)

GPIO.setup(SWITCH_UPPER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SWITCH_LOWER, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# You need to set up every channel you are using as an input or an output.
# sets the pin input/output setting to OUT, with initial value HIGH (ie. the relay is closed)
GPIO.setup(7, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(11, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(13, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(15, GPIO.OUT, initial=GPIO.HIGH)

try:
    while 1 >= 0:
        logger("Relaytest starting.")
        time.sleep(1)
        logger("PIN 16 to status: " + str(GPIO.input(16)))
        logger("PIN 18 to status: " + str(GPIO.input(18)))
        time.sleep(2)

        logger("PIN 7 to low")
        GPIO.output(7, GPIO.LOW)   # turns the first relay switch ON
        time.sleep(.5)             # pauses system for 1/2 second
        logger("PIN 7 to high")
        GPIO.output(7, GPIO.HIGH)  # turns the first relay switch OFF

        logger("PIN 11 to low")
        GPIO.output(11, GPIO.LOW)
        time.sleep(.5)
        logger("PIN 11 to high")
        GPIO.output(11, GPIO.HIGH)

        logger("PIN 13 to low")
        GPIO.output(13, GPIO.LOW)
        time.sleep(.5)
        logger("PIN 13 to high")
        GPIO.output(13, GPIO.HIGH)

        logger("PIN 15 to low")
        GPIO.output(15, GPIO.LOW)
        time.sleep(.5)
        logger("PIN 15 to high")
        GPIO.output(15, GPIO.HIGH)

        time.sleep(.5)
        logger("All PINs tested, pausing for 5 seconds.")
        time.sleep(5)

except KeyboardInterrupt:     # Stops program when "Control + C" is entered
    GPIO.cleanup()               # Turns OFF all relay switches
