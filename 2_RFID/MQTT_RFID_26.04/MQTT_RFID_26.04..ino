/******************************************************************************
MQTT_Switch_Example.ino
Example for controlling a light using an MQTT switch
by: Alex Wende, SparkFun Electronics

This sketch connects the ESP32 to a MQTT broker and subcribes to the topic
room/light. When the button is pressed, the client will toggle between
publishing "on" and "off".
******************************************************************************/

//Last modification in 26.04.19: Cards are working and sending information via MQTT. 

#include <WiFi.h>
#include <PubSubClient.h>
#include <SPI.h>
#include <MFRC522.h>
#define SS_PIN 33
#define RST_PIN 27
MFRC522 mfrc522(SS_PIN, RST_PIN);   // Create MFRC522 instance.
 

const char *ssid = "Test";   // name of your WiFi network
const char *password = "qwerty1234"; // password of the WiFi network

const byte LIGHT_PIN = 21;           // Pin to control the light with
const byte SWITCH_PIN = 14; 
const char *ID = "Boss1";  // Name of our device, must be unique
const char *SUB_TOPIC = "getPC";  // Topic to subcribe to
const char *PUB_TOPIC = "sendPC";  // Topic to publish the light state to
String previousID = "";

IPAddress broker(192,168,56,101); // IP address of your MQTT broker eg. 192.168.1.50
WiFiClient wclient;

PubSubClient client(wclient); // Setup MQTT client
bool state=0;

void callback(char* topic, byte* payload, unsigned int length) {
  String response;

  for (int i = 0; i < length; i++) {
    response += (char)payload[i];
  }
  Serial.println('\n');
  Serial.print("Message arrived ");
  Serial.print(topic);
  Serial.print(" ");
  Serial.println(response);
  digitalWrite(LIGHT_PIN, HIGH);
  delay(5000);
  digitalWrite(LIGHT_PIN, LOW);
    

}
// Connect to WiFi network
void setup_wifi() {
  Serial.print("\nConnecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password); // Connect to network

  while (WiFi.status() != WL_CONNECTED) { // Wait for connection
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

// Reconnect to client
void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect(ID)) {
      Serial.println("connected");
      Serial.print("Publishing to: ");
      Serial.println(PUB_TOPIC);
      Serial.println('\n');
      client.subscribe(SUB_TOPIC);
      Serial.println("connected");
      Serial.print("Subcribed to: ");
      Serial.println(SUB_TOPIC);
      Serial.println('\n');
      

    } else {
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200); // Start serial communication at 115200 baud
  pinMode(LIGHT_PIN,OUTPUT);  // Configure SWITCH_Pin as an input
  digitalWrite(LIGHT_PIN,LOW);  // enable pull-up resistor (active low)
  delay(100);
  setup_wifi(); // Connect to network
  client.setServer(broker, 1883);
  SPI.begin();      // Initiate  SPI bus
  mfrc522.PCD_Init();   // Initiate MFRC522
  client.setCallback(callback);
}

void sendMessage(){
  
  String content= "";
  byte letter;
  for (byte i = 0; i < mfrc522.uid.size; i++) 
  {
     content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : ""));
     content.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  if(!previousID.equals(content)){
    previousID=content;
    Serial.println();
    Serial.print("UID tag :");
    Serial.print(content.c_str());
    client.publish(PUB_TOPIC, content.c_str() ); 
    delay(1000);
  }
    // Halt PICC
  mfrc522.PICC_HaltA();

  // Stop encryption on PCD
  mfrc522.PCD_StopCrypto1();
}

void loop() {

 if (!client.connected())  // Reconnect if connection is lost
  {
    reconnect();
  }
  client.loop();
 if ( ! mfrc522.PICC_IsNewCardPresent()) 
  {
    previousID="";
    return;
  }
  // Select one of the cards
  if ( ! mfrc522.PICC_ReadCardSerial()) 
  {
    return;
  }
  sendMessage(); 

  
  }



/*
  if (!client.connected())  // Reconnect if connection is lost
  {
    reconnect();
  }
  client.loop();

  // if the switch is being pressed
  if(digitalRead(SWITCH_PIN) == 0) 
  {
    state = !state; //toggle state
    if(state == 1) // ON
    {
      client.publish(PUB_TOPIC, "on");
      Serial.println((String)PUB_TOPIC + " => on");
    }
    else // OFF
    {
      client.publish(PUB_TOPIC, "off");
      Serial.println((String)PUB_TOPIC + " => off");
    }

    while(digitalRead(SWITCH_PIN) == 0) // Wait for switch to be released
    {
      // Let the ESP handle some behind the scenes stuff if it needs to
      yield(); 
      delay(20);
    }
  }
}*/
