#include <WiFi.h>
#include <PubSubClient.h>

const char *ssid = "Test";   // name of your WiFi network
const char *password = "qwerty1234"; // password of the WiFi network

const byte LIGHT_PIN = 21;           // Pin to control the light with
const char *ID = "Boss1";  // Name of our device, must be unique
const char *TOPIC = "getPC";  // Topic to subcribe to
const char *STATE_TOPIC = "sendPC";  // Topic to publish the light state to

IPAddress broker(192,168,56,101); // IP address of your MQTT broker eg. 192.168.1.50
WiFiClient wclient;

PubSubClient client(wclient); // Setup MQTT client

// Handle incomming messages from the broker
void callback(char* topic, byte* payload, unsigned int length) {
  String response;

  for (int i = 0; i < length; i++) {
    response += (char)payload[i];
  }
  Serial.print("Message arrived ");
  Serial.print(topic);
  Serial.print(" ");
  Serial.println(response);
  if(response == "ON")  // Turn the light on
  {
    digitalWrite(LIGHT_PIN, HIGH);
    client.publish(STATE_TOPIC,"OK");
  }
  else if(response == "OFF")  // Turn the light off
  {
    digitalWrite(LIGHT_PIN, LOW);
    client.publish(STATE_TOPIC,"OK");
  }
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
    if(client.connect(ID)) {
      client.subscribe(TOPIC);
      Serial.println("connected");
      Serial.print("Subcribed to: ");
      Serial.println(TOPIC);
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
  pinMode(LIGHT_PIN, OUTPUT); // Configure LIGHT_PIN as an output
  delay(100);
  setup_wifi(); // Connect to network
  client.setServer(broker, 1883);
  client.setCallback(callback);// Initialize the callback routine
}

void loop() {
  if (!client.connected())  // Reconnect if connection is lost
  {
    reconnect();
  }
  client.loop();
}
