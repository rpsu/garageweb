
# DO NOT move the door, but just log stuff.
DRY_RUN=False

DEBUGGING=False

# Log levels:
# 0 = fairly quiet but actions and web requests recorded.
# 1 = increased logging
# 2 = record even door state every time it is queried
LogLevel = 1
VerboseConsole = False  # Wether or not print messages to console as well.
DoorPassword = "12345678"

# Close door automatically after seconds (if left fully opened)
# DoorAutoCloseDelay = 1200
DoorAutoCloseDelay = 480
# Door left open message after seconds (if left fully opened)
DoorOpenMessageDelay = 300

# Define which GPIO pins do what. Use GPIO.BOARD mode.
# Open and close may be the same or different.
PINS_BUTTON_OPEN = 11
PINS_BUTTON_CLOSE = 11
# Upper magnetic switch *closes* (value 0) when door is open.
SWITCH_UPPER = 18
# Upper magnetic switch *closes* (value 0) when door is closed.
SWITCH_LOWER = 16

# Door state constants.
STATE_UP = 'up'
STATE_DOWN = 'down'
STATE_BETWEEN = 'between'
