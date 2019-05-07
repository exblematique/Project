#define MY_DEBUG
#define MY_NODE_ID 3
//#define CONFIG_AUTOSTART_ARDUINO 1
/**********************************************
*     Ethernet Gateway Transport Defaults    */
#define MY_GATEWAY_MQTT_CLIENT
#define MY_GATEWAY_ESP32

/** Configuration of WiFi */
#define MY_WIFI_SSID "Test"
#define MY_WIFI_PASSWORD "qwerty1234"
#define MY_HOSTNAME "TestRight"

/** MQTT Configuration **/
#define MY_MQTT_PUBLISH_TOPIC_PREFIX "sendToPc"
#define MY_MQTT_SUBSCRIBE_TOPIC_PREFIX "getFromPc"
#define MY_MQTT_CLIENT_ID "Boss2"
#define MY_CONTROLLER_IP_ADDRESS 192, 168, 56, 101
#define MY_PORT 1883
/**********************************************/

//#define FASTLED_INTERNAL
//#include <FastLED.h>
//#include <ESP32Wifi.h>
#include <MySensors.h>
//#define MY_HOSTNAME "Boss2"

#define MY_BAUD_RATE 115200
#define OPEN 1
#define CLOSE 0
#define CHILD_ID 1

MyMessage msg;

uint8_t value = OPEN;

void presentation() {
  present(CHILD_ID, S_DOOR);
}

void setup(){
  Serial.begin(115200);
  /*Serial.println("Started clearing. Please wait...");
  for (uint16_t i=0; i<EEPROM_LOCAL_CONFIG_ADDRESS; i++) {
    hwWriteConfig(i,0xFF);
  }
  Serial.println("Clearing done.");*/
  msg.setType(V_TRIPPED);
  msg.setSensor(CHILD_ID);
}

void loop() {
  /*value = value == OPEN ? CLOSE : OPEN;
  send(msg.set(value));
  Serial.println("");
  delay(1000);
*/}

void receive(const MyMessage &msg)
{
  Serial.println("Smgth");
}
