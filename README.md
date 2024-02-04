# GarageWeb

This home automation tool is built to help garage access management and
door control. The project is not meant to be secure enough to be run 
exposed to the internet but should be protected by firewall if you wich
to be able to access it from outside. Setting up such network is outside 
the scope of this document.

This project was initially inspired by [Steve's video  "Raspberry Pi Controlled Garage Door & Sensor (complete instructions)" in Youtube](https://youtu.be/Fcx6wANw9KM). However it has been rewritten
to better support local testing and transportability. **RaspberryPi wiring is the same as in the video except there is a camera module present.**

## Usgae

For local Notifications you need HTTPS certificates (which browswers don't like but allow you to override the warnings). 

```sh
openssl req -x509 -newkey rsa:4096 -nodes -out garageweb/certs/cert.pem -keyout garageweb/certs/key.pem -days 365
```

This will generate certificates to `garageweb/certs` folder.

Then you can run this locally:

```sh
poetry run python garageweb/main.py [--debug]
```

## Configuration

The configuration is in file `garageweb/config.py`.

Override the door open/close password by writing it to a text file called
`garage-password.txt` in the root of this project. This file should contain only one line of text.
