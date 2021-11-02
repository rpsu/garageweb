import RPi.GPIO as GPIO
from datetime import datetime
import config
import os.path

fileName = os.path.basename(__file__)

# Read door status from magnetic switches connected to GPIO


def door_status():
    if GPIO.input(config.SWITCH_LOWER) == GPIO.HIGH and GPIO.input(config.SWITCH_UPPER) == GPIO.HIGH:
        if config.Debug == True:
            logger("Garage is Opening/Closing", fileName)
        return 'in-between'
    else:
        if GPIO.input(config.SWITCH_LOWER) == GPIO.LOW:
            if config.Debug == True:
                logger("Garage is Closed", fileName)
            return 'closed'

        if GPIO.input(config.SWITCH_UPPER) == GPIO.LOW:
            if config.Debug == True:
                logger("Garage is Open", fileName)
            return 'opened'


def logger(msg, fileName='??'):
    logfile = open("/home/pi/GarageWeb/static/log.txt", "a")
    logfile.write(datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S [" + fileName + "] - - " + msg + "\n"))
    logfile.close()
    if config.VerboseConsole == True:
        print(msg)
