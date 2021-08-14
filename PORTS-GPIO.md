# Raspberry PI board pins

## Magnetic switches

### Door closed when

        GPIO.input(16) == 0
        GPIO.input(18) == 1

### Door open when

        GPIO.input(16) == 1
        GPIO.input(18) == 0

### Door is in-between when

        GPIO.input(16) == 1
        GPIO.input(18) == 1

(ie. when both magnetic switches are open)

## Relay

### Open or close door

        # setup
        GPIO.setup(11, GPIO.OUT)
        # Trigger open/close circuit
        GPIO.output(11, GPIO.HIGH)
