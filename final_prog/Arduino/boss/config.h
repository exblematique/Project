#ifndef CONFIG_H
#define CONFIG_H

/* ---------------To setup table ------------------
 *  You need change only this file
 *  With the following variables:  
 */
#define TABLE_ID "3"
#define SSID_WIFI "Test"
#define PASSWORD_WIFI "qwerty1234"
#define MQTT_SERVER_IP 192, 168, 56, 101
#define MQTT_SERVER_PORT 1883         //The default port is 1883
/* ----------- The setup is finished -------------*/


#define FASTLED_INTERNAL
#include <FastLED.h>

#include "rfid.h"
#include "sensor-info.h"

// MySensors radio defines
#define MY_NODE_ID TABLE_SECTION_ID

// Table section ID set node id between 1-254
// You only need to change TABLE_ID
#define TABLE_SECTION_ID int(TABLE_ID)


// Enable the MY_DEBUG define to show debug messages
#define MY_DEBUG

/**************************************
*       Ethernet Configuration        *
***************************************/
#define MY_GATEWAY_MQTT_CLIENT
#define MY_GATEWAY_ESP32

/** Configuration of WiFi */
#define MY_WIFI_SSID SSID_WIFI
#define MY_WIFI_PASSWORD PASSWORD_WIFI
#define MY_HOSTNAME "Boss" TABLE_ID

/** MQTT Configuration **/
#define MY_MQTT_CLIENT_ID "Boss" TABLE_ID
#define MY_MQTT_PUBLISH_TOPIC_PREFIX "sendToPc/" TABLE_ID
#define MY_MQTT_SUBSCRIBE_TOPIC_PREFIX "getFromPc/" TABLE_ID
#define MY_CONTROLLER_IP_ADDRESS MQTT_SERVER_IP
#define MY_PORT MQTT_SERVER_PORT
/*************************************/


// Variables for serial communications
#define BAUDRATE 115200
#define TX_PIN 17
#define RX_PIN 16

// ESP32 helper reset pin
#define HELPER_RST_PIN A3

// Shared RFID reset pin
#define RFID_RST_PIN A0

// RFID data pins 
#define RFID0_SDA_PIN 13
#define RFID1_SDA_PIN 12
#define RFID2_SDA_PIN 27
#define RFID3_SDA_PIN 33

// Number of RFIDs on this Arduino
#define RFID_COUNT 4

// Delay in ms between RFID checks
#define RFID_CHECK_DELAY 75

// Led strip data pin
#define LEDSTRIP_DATA_PIN 14

// Led strip clock pin
#define LEDSTRIP_CLK_PIN 32

// Led strip type with clock pin (currently SK9822 is used, not APA102 even though it says on the label because of chinese clone manufacturers)
// if you do use APA102 make sure that they are not clones, because of the difference in CLOCK signals ------ you can add more types, see: https://github.com/FastLED/FastLED/wiki/Overview 
#define LEDSTRIP_TYPE SK9822
//define LEDSTRIP_TYPE APA102
//#define LEDSTRIP_TYPE WS2801
//#define LEDSTRIP_TYPE DOTSTAR

// Led strip types without clock pin ---- you can add more types, see: https://github.com/FastLED/FastLED/wiki/Overview
//#define LEDSTRIP_TYPE_WITHOUT_CLOCK WS2812
//#define LEDSTRIP_TYPE_WITHOUT_CLOCK WS2812B
//#define LEDSTRIP_TYPE_WITHOUT_CLOCK WS2811
//#define LEDSTRIP_TYPE_WITHOUT_CLOCK NEOPIXEL

// Number of flow_segments
#define FLOW_SEGMENT_COUNT 12

// Number of LEDs in each flow_segment
#define FLOW_SEGMENT_LENGTH 5

// Adjust brightness of LEDs
#define LED_BRIGHTNESS 20 

// Total number of LEDS
#define LED_COUNT (FLOW_SEGMENT_COUNT * FLOW_SEGMENT_LENGTH)

// Array of RFID sensors with grid positions
extern const SensorInfo sensor_info[];

// Create RFIDs
extern RFID RFIDs[];

// LED strip colors
extern CRGB off_color;
extern CRGB error_color;
extern CRGB voltage_colors[];
extern CRGB load_colors[];

// Edit module id if you want to edit test module
#define TEST_MODULE_ID 439560267

#endif
