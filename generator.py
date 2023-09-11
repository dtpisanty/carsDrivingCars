'''
A script that receives a car's OBD2 data through MQTT as a JOSN encoded string in the following format:
{"rpm":<float>,"speed":<float>,"runtime":<int (seconds)>,"pedal":<float>,"dist": <int (km)>"}
It uses this data to generate SVG drawings of simple cars made with triangles and boxes.
A new drawing is created everytime a 0 is received on the car/<carID>/status topic.

It's meant to be used with the obd2MQTT.py found at https://github.com/dtpisanty/carsDrivingCars
Make sure to use the same carID as an argument for both of these scripts.

Writen by Diego Trujillo Pisanty, August 2023
diego@trujillodiego.com
trujillodiego.com
'''

from Cars import Car
import paho.mqtt.client as mqtt
import json
from datetime import datetime
from argparse import ArgumentParser

dist0=None
maxSpeed=0
tDist=0
runtime=0
stalled=0
makeCar=False
idx=0

parser=ArgumentParser()
parser.add_argument('-c', '--carID', nargs='?', const='car_', help='unique identifier for current car')
args = parser.parse_args()
carID="car_" # Define a UID for MQTT. Must be different for every car
if args.carID is None:
    carID+=str(randint(0,99))
    print('Using random car ID {}'.format(carID))
elif args.carID == 'car_':
    carID+=str(randint(0,99))
    print('Using random car ID {}'.format(carID))
else:
    carID=args.carID
    print('Using carID: {}'.format(carID))

# MQTT broker info
host="" # Fill with broker address
port=1883
mqttc=mqtt.Client('svgClient')

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT result code "+str(rc))
    client.subscribe([("car/{}/status".format(carID),2),("car/{}/sensors".format(carID),2)])

def on_message(client, userdata, msg):
    global dist0,maxSpeed,tDist,runtime,stalled,makeCar
    print(msg.topic+" "+str(msg.payload))
    if 'status' in msg.topic:
        # Makes a new drawing when car is turned off
        if int(msg.payload)==0:

            makeCar=True
    if 'sensors' in msg.topic:
        data=json.loads(msg.payload)
        runtime=data['runtime']/60.0
        if int(data['speed'])==0:
            stalled+=1
        else:
            maxSpeed=max(maxSpeed,data['speed'])
        if not dist0:
            dist0=data['dist']
        else:
            tDist=data['dist']-dist0
mqttc.on_connect=on_connect
mqttc.on_message=on_message
mqttc.connect(host,port,60)

while True:
    if makeCar:
        c=Car(tDist,maxSpeed,stalled/60,int(runtime),maxDist=40,maxTime=165)
        c.idx=idx
        idx+=1
        filename=datetime.now().strftime('%Y%m%d%H%M%S')+'.svg'
        c.render(filename)
        print("saved: "+filename)
        # Reset trip variables
        dist0=None
        maxSpeed=0
        tDist=0
        runtime=0
        stalled=0
        makeCar=False
    mqttc.loop()