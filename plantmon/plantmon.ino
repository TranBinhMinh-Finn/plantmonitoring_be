#include <ArduinoJson.h>
#include <ArduinoJson.hpp>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <WiFiManager.h>

#define ONE_WIRE_BUS D12
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

const char* ssid = "Wifinn";
const char* password = "binhminh2000";
const char* mqtt_server = "fe9f73567a7b41ee9b74970983a82aa2.s2.eu.hivemq.cloud";
const char* mqtt_username = "plantmon";
const char* mqtt_password = "RZF3SfTcf8Wg9s";

const char* deviceId = "3a4d7cdf-4b13-4616-9213-30e02b028646";

WiFiClientSecure wifiClient;
PubSubClient client(wifiClient);
#define MSG_BUFFER_SIZE	(50)
char msg[MSG_BUFFER_SIZE];
int value = 0;

void setup_wifi_manager()
{
  WiFiManager wm;

  bool res;
  // res = wm.autoConnect(); // auto generated AP name from chipid
  // res = wm.autoConnect("AutoConnectAP"); // anonymous ap
  res = wm.autoConnect("AutoConnectAP","password"); // password protected ap

  if(!res) {
      Serial.println("Failed to connect");
      // ESP.restart();
  } 
  else {
    //if you get here you have connected to the WiFi    
    Serial.println("connected...yeey :)");
  }
}
void setup_wifi() {

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

int thresholdValue = 800;
int rainPin = A0;
int lightPin = D13;

void setup_sensors(){
  pinMode(rainPin, INPUT);
  sensors.begin();
}

const char* manual = "MAN";
const char* timed = "TIM";
const char* adaptive = "ADT";
int watering_mode = 0;
int water_interval = 5 * 60;
const char* manual_command = "water";
const char* update_command = "update";

// process incoming messages from the message queue

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
      
    water_interval = interval * 60;
  }
  //for (int i = 0; i < length; i++) {
  //  Serial.print((char)payload[i]);
  //}
  Serial.println();

}

// Connect to MQTT Broker

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str(), mqtt_username, mqtt_password)) {
      Serial.println("connected");
      client.subscribe("commands");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}
// Configurations to get time from ntp server
const char* ntpServer = "pool.ntp.org";
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org");


// Relay pin is controlled with D2. The active wire is connected to Normally Closed and common
int relay = D2;
volatile byte relayState = LOW;

void setup() {
  pinMode(BUILTIN_LED, OUTPUT);     // Initialize the BUILTIN_LED pin as an output
  pinMode(lightPin, INPUT);

  pinMode(relay, OUTPUT);

  Serial.begin(115200);
  setup_wifi_manager();
  setup_sensors();
  wifiClient.setInsecure();
  client.setServer(mqtt_server, 8883);
  client.setCallback(callback);
  timeClient.begin();
  timeClient.setTimeOffset(0);
}

time_t lastMsg = 0;
time_t lastWatered = 0;

// Timer Variables
long lastDebounceTime = 0;  
long debounceDelay = 10000;

// Send Command to relay to water
void water(){
  digitalWrite(relay, HIGH);
  delay(5000);
  digitalWrite(relay, LOW);
}


void loop() {
  //get sensor values
  int sensorValue = analogRead(rainPin);
  Serial.print("moisture:");
  float moisture = (1024 - sensorValue) * 1.0 / (1024 - 500) * 100.0; 
  Serial.println(moisture);
  
  sensors.requestTemperatures();  
  Serial.print("temperature:");
  float temp = sensors.getTempCByIndex(0);
  Serial.println(temp);

  int light_level = digitalRead(lightPin); 
  Serial.print("light:");
  Serial.println(light_level);

  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  timeClient.update();

  time_t epochTime = timeClient.getEpochTime();
  Serial.print("Epoch Time: ");
  Serial.println(epochTime);
  //publish to message queue
  if (epochTime - lastMsg >= 60 || lastMsg == 0) {
    lastMsg = epochTime;
    char buffer[1024];
    DynamicJsonDocument doc(1024);
    doc["device"] = deviceId;
    doc["humidity"] = moisture;
    doc["temperature"] = temp;//sensors.getTempCByIndex(0);
    doc["brightness"] = 1-light_level;
    doc["timestamp"] = (int)epochTime;
    size_t n = serializeJson(doc, buffer);
    client.publish("readings", buffer, n);
    //snprintf (msg, MSG_BUFFER_SIZE, "moisture: %d", sensorValue);
    Serial.print("Published message. ");
    //Serial.println(msg);
  }
  if(watering_mode == 1)
  if(epochTime - lastWatered >= water_interval || lastWatered == 0)
  {
    water();
    lastWatered = epochTime;
  }
  if(watering_mode == 2)
  if(moisture < 30.0 && temp < 30)
  {
    water();
  }
  delay(5000);
}
