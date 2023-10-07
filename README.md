# Cars Driving Cars
*Cars Driving Cars* is a project that promotes reflection about car use by extracting vehicles' data and using it to generate graphics and to move toy cars on a racetrack. 
This repository contains scripts to (1) Read car data through OBD2 and transmit it via MQTT, (2) generate drawings of cars based on trip data, and (3) receive car data on an 
ESP32 board and us it to drive toy cars. 

![carGrid](https://github.com/dtpisanty/carsDrivingCars/assets/57118670/4394ea0f-af37-424d-8104-115e859d312d)

# Extracting car data
Realtime car data can be extracted using ELM327 OBD2 compatible readers. The code in this project has been tested using a USB reader connected to a Raspberry Pi Zero W.
To access the OBD2 interface make sure your user is part of the dialout group by running:

```usermod -a -G dialout $USER```

It should also be posible to use bluetooth ELM327 readers by configuring `rfcomm` but this hasn't been tested.

## obd2mqtt.py
This script uses python-obd to read car data and paho-mqtt to send it via MQTT. It takes the ```--carID``` or ```-c``` argument to set a car ID. It's important 
to do this as it will set the MQTT publish topics which are used by other scripts so this ID must be noted. MQTT broker data needs to be hardcoded inside of the
script under the host and port variables.

### Dependencies
Install both python-obd and paho-mqtt with pip using:
```pip install obd paho-mqtt```

### Running
To run the script type: ```python obd2mqtt.py -c car1``` where `car1` is the carID you wish to use.

The current version of obd2mqtt.py crashes on broken connections. Make sure you have an internet connection (usually made through a mobile phone's hotspot),
that your OBD reader is connected to the car, and that the car is turned on before running this script.  A setup like the following should work:
![gear](https://github.com/dtpisanty/carsDrivingCars/assets/57118670/18331656-d66e-4852-8674-aa825b8c6689)

#### Arguments
* --carID or -c: A string used to name the current car. It will be used to produce MQTT publish topics. If none is provided then a random one will be used.
* --port or -p: Serial port to use for reading OBD data. Default is `/dev/ttyUSB0`

# Generating SVG drawings
The __generator.py__ script will subscribe to the MQTT topics that __obd2mqtt.py__ publishes to and will generate a new drawing everytime the car is shut off.
The program uses each trip's travel distance, duration, stalled time (% of time spent at 0 km/h) and maximum speed to determine the geometry and colour of each
drawing.

Make sure to use the same ```--carID``` or ```-c``` argument as when running obd2mqtt.py to guarantee succesful subscription.

MQTT broker address and port are hardcoded in this file.

# Interactive visualisation
There is a P5.js enabled visualisation within the interactive folder. This reads geometry points from a JSON file. This geometry matches the generated
SVG files made by __generator.py__ and interpolates between different graphics depending on the mouse's x-position. To run it use a local server (such 
as LAMP, WAMP, MAMP) or an IDE with live HTML/JS view (such as brackets).
![interactiveStill](https://github.com/dtpisanty/carsDrivingCars/assets/57118670/fa1dc401-6dae-4a41-a8e5-c40192f307c6)

# Driving toy cars (and other electronics)
To control toy cars on electric tracks using a real car's accelerator pedal position (or any other parameter) refer to __trackControl.ino__. This program
is meant to be loaded to an ESP32 board through the Arduino IDE and uses data received through MQTT from __obd2mqtt.py__ to set PWM frequencies on pins 4 and 5.
Ideally these  signals drive transistors or MOSFETS connected to the toy racetrack (or other DC electronics) to control the cars' speed. The following schematic
should provide some guidance:

![schematic](https://github.com/dtpisanty/carsDrivingCars/assets/57118670/c3724ccc-aa27-4ef2-b2a2-0af9492af606)

The circuit connected to an electric race track should look something like this:
![circuitWeb](https://github.com/dtpisanty/carsDrivingCars/assets/57118670/dd1b7a22-eebb-45ee-bd89-e5893f084d17)

This program can subscribe to two different carIDs to drive two separete channels. WiFi credentials, carIDs, MQTT broker address and port are all
hardcoded and need to be filled in before uploading the program.

### Dependencies
The __trackControl.ino__ sketch depends on the [PubSubClient](https://github.com/knolleary/pubsubclient) library for MQTT communication. This can be
installed through the Arduino library manager.
