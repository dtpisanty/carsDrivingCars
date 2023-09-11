'''
A script that reads a car's OBD2 data from an ELM327
adapter. This initial version has been tested with USB
adapters on Ubuntu 22.04 and ona a Raspberry Pi Zero 
running Raspberry Pi OS.

Usage:
Make sure your computer has an internet connection
and that the OBD2 adapter is pluged-in before 
running this code.

Writen by Diego Trujillo Pisanty, August 2023
diego@trujillodiego.com
trujillodiego.com
'''
import obd
import paho.mqtt.client as mqtt
from time import sleep
from argparse import ArgumentParser
from random import randint

# Define CLI arguments
parser=ArgumentParser()
parser.add_argument('-c', '--carID', nargs='?', const='car_', help='unique identifier for current car')
parser.add_argument('-p', '--port', nargs='?', const='/dev/ttyUSB0', help='serial port / BT port to use')
args = parser.parse_args()
carID="car_" # Define a UID for MQTT. Must be different for every car
if args.carID is None:
    carID+="_"+str(randint(0,99))
    print('Using random car ID {}'.format(carID))
elif args.carID == 'car_':
    carID+="_"+str(randint(0,99))
    print('Using random car ID {}'.format(carID))
else:
    carID=args.carID
    print('Using carID: {}'.format(carID))

# MQTT broker info
host="" # Add your broker address here
port=1883
mqttc=mqtt.Client(carID)

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT result code "+str(rc))
    client.publish("car/{}/status".format(carID),"1",2)

mqttc.on_connect=on_connect
mqttc.will_set("car/{}/status".format(carID),"0",2)
mqttc.connect(host,port,60)
sensorsTopic="car/{}/sensors".format(carID)

#OBD2 commands
rpmCode=obd.commands[1][int("0x0C",0)]
speedCode=obd.commands[1][int("0x0D",0)]
distanceCode=obd.commands[1][int("0x31",0)]
runtimeCode=obd.commands[1][int("0x1F",0)]
accelPosCode=obd.commands[1][int("0x4A",0)]
connection=obd.OBD()


while connection.status()==obd.OBDStatus.CAR_CONNECTED:
    mqttc.loop()
    #check rpm
    resp=connection.query(rpmCode)
    rpm=resp.value.magnitude
    #check speed
    resp=connection.query(speedCode)
    speed=resp.value.magnitude
    #check pedal pos
    resp=connection.query(runtimeCode)
    runtime=resp.value.magnitude
    #check pedal pos
    resp=connection.query(accelPosCode)
    pedalPos=resp.value.magnitude
    #check distance
    resp=connection.query(distanceCode)
    distance=resp.value.magnitude
    #Assemble JSON
    jsonMsg="\"rpm\":{revs},\"speed\":{spd},\"runtime\":{rtime},\"pedal\":{pos},\"dist\":{dist}".format(revs=rpm,spd=speed,rtime=runtime,pos=pedalPos,dist=distance)
    jsonMsg="{"+jsonMsg+"}"
    print(jsonMsg)
    mqttc.publish(sensorsTopic,jsonMsg)
    sleep(1)
    print(rpm,speed,pedalPos,distance)