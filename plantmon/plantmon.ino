#include <ArduinoJson.h>
#include <ArduinoJson.hpp>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <WiFiManager.h>
#include "math.h"

/// ports config
#define ONE_WIRE_BUS D12
#define MUX_BUS A0
#define MUX_A D8
// Relay pin is controlled with D2. The active wire is connected to Normally Closed and common
#define RELAY D2
volatile byte relayState = LOW;

// DS18B20 Onewire config
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// MQTT client config
const char* mqtt_server = "fe9f73567a7b41ee9b74970983a82aa2.s2.eu.hivemq.cloud";
const char* mqtt_username = "plantmon";
const char* mqtt_password = "RZF3SfTcf8Wg9s";

// MQTT constants & variables
const char* deviceId = "ffc5007b-d629-4c0f-9711-dc9aff3630c8";
WiFiClientSecure wifiClient;
PubSubClient mqttClient(wifiClient);
#define MSG_BUFFER_SIZE	(50)
char msg[MSG_BUFFER_SIZE];
int value = 0;


// Connect to a Wifi router via Wifi Manager 
void setup_wifi_manager()
{
  WiFiManager wm;

  bool res;
  // res = wm.autoConnect(); // auto generated AP name from chipid
  // res = wm.autoConnect("AutoConnectAP"); // anonymous ap
  // wm.setConnectTimeout(90000);
  res = wm.autoConnect("Plantmon","password"); // password protected ap

  if(!res) {
      Serial.println("Failed to connect");
      // ESP.restart();
  } 
  else {
    //if you get here you have connected to the WiFi    
    Serial.println("connected...yeey :)");
  }

}


void setup_ports(){
  pinMode(MUX_BUS, INPUT);
  pinMode(RELAY, OUTPUT);
  pinMode(MUX_A, OUTPUT);
}

// Send Command to relay to water
void water(void){
  static bool started = false;
  while(started);
  digitalWrite(RELAY, HIGH);
  delay(300);
  digitalWrite(RELAY, LOW);
}


// Message constants 
const char* manual = "MAN";
const char* timed = "TIM";
const char* adaptive = "ADT";
const char* manual_command = "water";
const char* update_command = "update";

// Watering modes
int watering_mode = 0;
int water_interval = 5;

// Process incoming messages from the message queue
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.println("] ");
  DynamicJsonDocument doc(1024);
  deserializeJson(doc, payload);
  const char* id = doc["device"];
  if(strcmp(id, deviceId)!=0)
    return ;
  const char* command = doc["command"];
  if(strcmp(command, manual_command)==0)
    water();
  if(strcmp(command, update_command)==0)
  {
    const char* mode = doc["watering_mode"];
    int interval = doc["time_interval"];
    Serial.println(interval);
    if(strcmp(mode, manual)==0)
    {
      Serial.println("switch to manual");
      watering_mode = 0;
    }
    else if(strcmp(mode, timed)==0)
    {
      watering_mode = 1;
      Serial.println("switch to timed");      
    }
    else
    {
      watering_mode = 2;
      Serial.println("switch to adaptive");
    }
      
    water_interval = interval;
  }
  //for (int i = 0; i < length; i++) {
  //  Serial.print((char)payload[i]);
  //}
  Serial.println();

}

// Connect to MQTT Broker
void reconnect() {
  // Loop until we're reconnected
  while (!mqttClient.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (mqttClient.connect(clientId.c_str(), mqtt_username, mqtt_password)) {
      Serial.println("connected");
      mqttClient.subscribe("commands");
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

// Configurations to get time from ntp server
const char* ntpServer = "asia.pool.ntp.org";
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org");

void setup() {
  Serial.begin(115200);
  setup_ports();
  sensors.begin();

  delay(200);
  setup_wifi_manager();

  wifiClient.setInsecure();

  delay(200);

  mqttClient.setServer(mqtt_server, 8883);
  mqttClient.setCallback(callback);

  delay(200);

  timeClient.begin();
  timeClient.setTimeOffset(0);
}


void publishReadings(float temperature, float moisture, float brightness, long epochTime)
{
  char buffer[1024];
  DynamicJsonDocument doc(1024);
  doc["device"] = deviceId;
  doc["humidity"] = moisture;
  doc["temperature"] = temperature;
  doc["brightness"] = brightness;
  doc["timestamp"] = epochTime;
  size_t n = serializeJson(doc, buffer);
  mqttClient.publish("readings", buffer, n);
  //snprintf (msg, MSG_BUFFER_SIZE, "moisture: %d", sensorValue);
  Serial.println("Published message. ");
  //Serial.println(msg);
}

const long MSG_INTERVAL = 5000;
long lastMsg = 0;
long lastWatered = 0;


const int LUX_CALC_SCALAR = 101.905;
const float LUX_CALC_EXPONENT = -0.9;


float luxConversion(int reading)
{
  // Serial.println(reading);
  float VoutLDR = float(reading) * 5 / float(1023);// Conversion analog to voltage
  float RLDR = (10000.0 * 5) / (5 - VoutLDR) - 10000.0; // Conversion voltage to resistance
  // Serial.println(RLDR);
  float lux = pow(10, -2 * (log10(RLDR/1000) - 1.905));
  return lux;
}

void loop() {
  unsigned long now = millis();
  
  //get sensor values

  // read MUX channel 001
  digitalWrite(MUX_A, HIGH);
  delay(10);
  int sensorValue1 = analogRead(MUX_BUS);
  
  // read MUX channel 000
  digitalWrite(MUX_A, LOW);
  delay(10);
  int sensorValue0 = analogRead(MUX_BUS); 

  // read from DS18B20
  sensors.requestTemperatures();  
  float temp = sensors.getTempCByIndex(0);

  // conversions
  float moisture = (1024 - sensorValue1) * 1.0 / (1024 - 500) * 100.0; 

  float brightness = luxConversion(sensorValue0);// Conversion resitance to lumen  //(1024 - sensorValue0) * 1.0 / (1024) * 100.0; 
  
  // watering mode
  if(watering_mode == 1)
  if(now - lastWatered >= water_interval || now < lastWatered)
  {
    water();
    lastWatered = now;
  }
  if(watering_mode == 2)
  if(moisture < 15.0 && temp < 35)
  {
    water();
  }

  // mqtt subscribe loop
  if (!mqttClient.connected()) {
    reconnect();
  }
  mqttClient.loop();

  

  // debugging
  Serial.print("moisture:");
  Serial.print(moisture);
  Serial.print(" - ");
  Serial.print(sensorValue1);
  
  Serial.print(" light:");
  Serial.print(brightness);
  Serial.print(" - ");
  Serial.print(sensorValue0);

  Serial.print(" temperature:");
  Serial.print(temp);

  Serial.println();

  if(now - lastMsg > MSG_INTERVAL || now < lastMsg)
  {
    timeClient.update();
    long epochTime = timeClient.getEpochTime();

    Serial.print(" Epoch Time: ");
    Serial.println(epochTime);

    if (!mqttClient.connected()) {
      reconnect();
    }
    publishReadings(temp, moisture, brightness, epochTime);
    lastMsg = now;
  }
}
