# carsDrivingCars
Cars Driving Cars is a project that promotes reflection about car use by extracting vehicles data, abstracing it into simple geometry and using it to move toy cars on a racetrack. 
This repository contains scripts to (1) Read car data through OBD2 and transmit it via MQTT. (2) Generate drawings of cars based on trip data and (3) Receive car data on an 
ESP32 board and us it to drive toy cars.

# Extracting car data
Realtime car data can be extracted using ELM327 OBD2 compatible readers. The code in this project has been tested using a USB reader connected to a Raspberry Pi Zero W.
For this to work make sure your user is part of the dialout group by running:

```usermod -a -G dialout $USER```

It should also be posible to use bluetooth ELM327 readers by configuring rfcomm but this hasn't been tested.

## obd2mqtt.py
This script uses python-obd to read car data and paho-mqtt to send it via MQTT. It takes the ```--carID``` or ```-c``` argument to set a car ID. It's important 
to do this as it will set the MQTT publish topics which are used by other scripts so this ID must be noted. MQTT broker data needs to be hardcoded inside of the
script under the host and port variables.

# Generating SVG drawings
The __generator.py__ script will subscribe to the MQTT topics that __obd2mqtt.py__ publishes to and will generate a new drawing everytime the car is shut off.
The program uses each trips travel distance, duration, stalled time (% of time spent at 0 km/h) and maximum speed to determine the geometry of each drawing.
Make sure to use the same ```--carID``` or ```-c``` argument as when running obd2mqtt.py to guarantee succesful subscription.

Once again MQTT broker address and port are hardcoded in this file.

# Driving toy cars (and other electronics)
To control toy cars on electric tracks using a real car's accelerator pedal position (or any other parameter) refer to __trackControl.ino__. This program
is meant to be loaded to an ESP32 board and uses data received through MQTT from __obd2mqtt.py__ to set PWM frequencies on pins 4 and 5. Ideally these 
signals drive transistors or MOSFETS connected to the toy racetrack (or other DC electronics) to control the cars' speed.

This program can subscribe to two different carIDs to drive two separete channels. WiFi credentials, carIDs, MQTT broker address and port are all
hardcoded and need to be filled in before uploading the program.
