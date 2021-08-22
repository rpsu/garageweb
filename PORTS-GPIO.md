# Raspberry PI board pins

GPIO (General Purpose Input/Output) PINs are well explained on Raspberry Pi documentation, 
[https://www.raspberrypi.org/documentation/computers/os.html#gpio-and-the-40-pin-header](https://www.raspberrypi.org/documentation/computers/os.html#gpio-and-the-40-pin-header).

GPIO in Python documentation and some examples are in [](https://sourceforge.net/p/raspberry-gpio-python/wiki/BasicUsage/).

**In this project we use BOARD mode (`GPIO.setmode(GPIO.BOARD)`) ie. the GPIO port numbers will follow the smaller, ordered numbers on the board, "Physical/Board". See [](https://pinout.xyz) for detailed info of all the PINs. In the picture below here the numbers are displayed in the middle of the right hand side graph, inside the white circles.

![Raspberry Pi PIN (source https://raspberrypi.org documentation)](https://www.raspberrypi.org/documentation/computers/images/GPIO-Pinout-Diagram-2.png)

Controlling PINS their input/output: [](https://www.raspberrypi.org/documentation/computers/os.html#gpio-in-python)

`gpiozero` tool which is installed by default: [](https://gpiozero.readthedocs.io/en/stable/)

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
