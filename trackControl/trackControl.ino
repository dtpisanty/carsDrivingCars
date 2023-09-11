/*
This program controls an electric race car track by
replacing the provided resistive controllers with a PWM 
signals fed through TIP120 transistors. It uses pins 4
and 5 on an ESP32 Dev Module to drive two cars through
MQTT messages.

The MQTT client subsribes to car/car1id/sensors and 
car/car2id/sensors where the carIDs can be defined through
the provided variables. The callback function expect to 
receive a JSON string with a "pedal" property followd by
a position argument. The simplest JSON this program will 
parse is "{"pedal":<float>}". This JSON will usually be 
generated from real car data by the obd2MQTT.py script
found in https://github.com/dtpisanty/carsDrivingCars.

CIRCUIT
ESP32 | TIP 120  | TRACK CONTROL
GND --> Emitter ---> GND
D4 ---> Base 
        Collector -> 5V 

GND --> Emitter ---> GND
D5 ---> Base 
        Collector -> 5V 

Written by Diego Trujillo Pisanty, August 2023.
diego@trujillodiego.com
trujillodiego.com
*/

#include "WiFi.h"
#include <PubSubClient.h>
#define debug false

//WiFi
// Enter your network's name
const char* ssid = "";
//... and password
const char* password = "";

//Car variables
String car1Id = "car1";
String car2Id = "car2";
const int car1Pin = 4;
const int car2Pin = 5;
float pedalPos1 = 0;
float pedalPos2 = 0;

// setting PWM properties
const int freq = 75000;
const int car1Channel = 0;
const int car2Channel = 1;
const int resolution = 10;


void setup_wifi() {
  delay(5);
#if debug
  Serial.println();
  Serial.print("Connecting to");
  Serial.println(ssid);
#endif
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
#if debug
    Serial.print(".");
#endif
  }
#if debug
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("Local IP: ");
  Serial.println(WiFi.localIP());
#endif
}

//MQTT
//Enter your MQTT broker's address
const char* mqtt_server = "";
//Default port is 1883
const int port = 1883;
WiFiClient espClient;
PubSubClient cliente(espClient);
//LED on pin 2 will turn on when MQTT is connected
const int statLed = 2;

void reconnect() {
  // Loop until we're reconnected
  while (!cliente.connected()) {
    digitalWrite(statLed, LOW);
#if debug
    Serial.print("Attempting MQTT connection...");
#endif
    // Create a random client ID
    String clientId = "carTrack-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect and set will message on "car/track/status" to 0
    if (cliente.connect(clientId.c_str(), "car/track/status", 2, false, "0")) {
#if debug
      Serial.println("MQTT connected");
#endif
      // Once connected, publish an announcement...
      cliente.publish("car/track/status", "1");
    } else {
#if debug
      Serial.print("Error, code=");
      Serial.print(cliente.state());
      Serial.println("retrying in 3 sec");
#endif
      // Wait 5 seconds before retrying
      delay(3000);
    }
  }
  //Define MQTT topics based on carID
  String strTopic1 = "car/" + car1Id + "/sensors";
  String strTopic2 = "car/" + car2Id + "/sensors";
  char topic1[strTopic1.length()];
  strTopic1.toCharArray(topic1, strTopic1.length());
  char topic2[strTopic2.length()];
  strTopic2.toCharArray(topic2, strTopic2.length());
  //Subscribe to topics
  cliente.subscribe(topic1);
  cliente.subscribe(topic2);
  digitalWrite(statLed, HIGH);
#if debug
  Serial.println("Subscribed to car/" + car1Id + "/sensors");
  Serial.println("Subscribed to car/" + car2Id + "/sensors");
#endif
}

void callback(char* topic, byte* payload, unsigned int length) {
  //Callback function that runs when a message is received
#if debug
  Serial.print("Messege @ topic: ");
  Serial.println(topic);
  Serial.print(" Len: ");
  Serial.println(length);
#endif
  String strTopic = String(topic);
  char inMsg[length];
  for (int i = 0; i < length; i++) {
    inMsg[i] = payload[i];
  }
  String strPayload = String(inMsg);
  //Extract pedal position from received JSON
  int pedalStart = strPayload.indexOf("l");
  int pedalEnd = strPayload.indexOf(",", pedalStart);
  String strPedal = strPayload.substring(pedalStart + 3, pedalEnd);
  strPedal.trim();
#if debug
  Serial.println(strPayload);
  Serial.print("Pedal ");
  Serial.print(strPedal);
  Serial.print(" l:");
  Serial.println(strPedal.length());
#endif
  // Extract pedal positions for car1 and car2
  if (strTopic.indexOf(car1Id) > 0) {
    pedalPos1 = strPedal.toFloat();
    if (pedalPos1 < 9.5) {
      pedalPos1 = 0;
    }
#if debug
    Serial.print(car1Id);
    Serial.println(pedalPos1);
#endif
  } else if (strTopic.indexOf(car2Id) > 0) {
    pedalPos2 = strPedal.toFloat();
    if (pedalPos2 < 9.5) {
      pedalPos2 = 0;
    }
#if debug
    Serial.print(car2Id);
    Serial.println(pedalPos2);
#endif
  }
}


// SETUP
void setup() {
#if debug
  Serial.begin(115200);
#endif
  // PWM
  // configure PWM functionalitites
  ledcSetup(car1Channel, freq, resolution);
  ledcSetup(car2Channel, freq, resolution);
  // attach the channel to the GPIO to be controlled
  ledcAttachPin(car1Pin, car1Channel);
  ledcAttachPin(car2Pin, car2Channel);
  //WiFi and MQTT setup
  pinMode(statLed, OUTPUT);
  setup_wifi();
  cliente.setServer(mqtt_server, port);
  cliente.setCallback(callback);
}

void loop() {
  //If WiFi is disconnected attempt re-connect
  if (WiFi.status() != WL_CONNECTED) {
    setup_wifi();
  }
  //If MQTT is disconnected attempt re-connect
  if (!cliente.connected()) {
    reconnect();
  }
  cliente.loop();
  //Compute car speeds based on received position
  unsigned int speed1 = 0;
  unsigned int speed2 = 0;
  if (pedalPos1 >= 9.5) {
    speed1 = map(pedalPos1, 9.5, 45, 800, 1023);
#if debug
    Serial.print(car1Id);
    Serial.println(speed1);
#endif
  }
  if (pedalPos2 >= 9.5) {
    speed2 = map(pedalPos2, 9.5, 45, 800, 1023);
#if debug
    Serial.print(car2Id);
    Serial.println(speed2);
#endif
  }
  //Generate PWM output based on speed
  ledcWrite(car1Channel, speed1);
  ledcWrite(car2Channel, speed2);
}
