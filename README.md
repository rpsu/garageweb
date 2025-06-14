# Garage web controller

This project is based on https://github.com/shrocky2/GarageWeb repository even if modified. That's where most of the credit should go!

Also: I'm rewriting the instructions after heavy modifications of the system which does contain a door monitor to ensure the door will not remain open after my kids forget about closing the door. Hence there is a (configurable) delay how long the door will keep fully open before the monitoring closes it.

---

YouTube Video Instructions found here: https://youtu.be/Fcx6wANw9KM

Setting up a Flask web server to control your garage door & display the door status & log usage on your own web.

The service runs on port 5000 but do not expose it to the world. Rather setup a proxy with some authentication mechanism between outside and your Pi, for example Nginx with Basic Authentication.

Also you should read carefully how to configure a proper password for opening/closing the door.

--------------------------------------------------------------------
Products I used in this video:
--------------------------------------------------------------------

Raspberry Pi Zero W with case on Amazon: https://amzn.to/34ujK5C

Raspberry Pi Zero W on Adafruit: https://www.adafruit.com/product/3400

4 Channel Relay (to Open Garage Door): https://amzn.to/3b4lHbD

Magnetic Reed Switch (You need 2): https://amzn.to/39YG7kU

Jumper/Breadboard wire 120ct: https://amzn.to/2V3fFlV

Hammer Header & Install Kit on Amazon: https://amzn.to/3b5RbxX

Hammer Headers on Adafruit: https://www.adafruit.com/product/3662

--------------------------------------------------------------------
**(incomplete rewrite - work in progress)** Setup Instructions:
--------------------------------------------------------------------

1.  --First setup your Raspberry Pi: https://www.youtube.com/watch?v=EeEU_8HG9l0 
2.  --Lets upgrade the apt-get program: 
sudo apt-get update

1.  --Next install the Flask Web Server and some more `python3` packages (the 2nd line assuming your Pi is Zero): 
sudo apt-get install python3
sudo apt-get install python3-gpiozero # depending your Pi version this might be something else
sudo apt-get install python3-flask python3-dotenv

1.  --Install the GIT application so you can download my Github code: 
sudo apt-get install git 

1.  --Download my Github code: 
sudo git clone https://github.com/rpsu/GarageWeb
 
1.  --Test out setup and webpage (default port is 5000)
cd GarageWeb
     --Test Relay connections
python3 relaytest.py
     --Test Magnetic Reed Switches
python3 log.py
     --Test out Webpage (Rasp_Pi_IP_Address:5000)
python3 web3.py


 1.  --To Setup this code to run automatically on system boot up:
sudo nano /etc/rc.local
     --Add the next 2 lines before the last line "exit 0"
sudo python /home/pi/GarageWeb/web.py &
sudo python /home/pi/GarageWeb/log.py &
exit 0

1.  --Change the default password of "12345678"
sudo nano web.py
     --find the 2 lines that contain "12345678" change to new password.

1.  --Change default port number (if desired) it'll be the last line of web.py

2.   --Reboot system and let program autostart
sudo reboot

1.   --Set up Port Forwarding on your Router to allow access when away from home.
     --Once setup, turn off WiFi on your phone and test. You'll need to know the REAL address of your home router.

--------------------------------------------------------------------
Wiring Diagram:
--------------------------------------------------------------------

<img src="https://github.com/rpsu/GarageWeb/blob/main/Wiring_Diagram.jpg">

--------------------------------------------------------------------
Additional Videos:
--------------------------------------------------------------------
Sonoff Garage Door Opener: https://youtu.be/f1JeKHraDf8

How to set up your Raspberry Pi: https://youtu.be/EeEU_8HG9l0

How to set up Port Forwarding on your Router: https://youtu.be/VhVV25zCFrQ
