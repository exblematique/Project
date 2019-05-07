#ifndef CONFIG_H
#define CONFIG_H

#define CONFIG_AUTOSTART_ARDUINO 0

#define FASTLED_INTERNAL
#include <FastLED.h>

#include "rfid.h"
#include "sensor-info.h"

// Enable the MY_DEBUG define to show debug messages
#define MY_DEBUG

/**************************************
* Ethernet Gateway Transport Defaults
* To use network, use the library <Ethernet.h>
***************************************/
#define MY_GATEWAY_MQTT_CLIENT
#define MY_GATEWAY_ESP32

/** Configuration of WiFi */
#define MY_WIFI_SSID "Test"
#define MY_WIFI_PASSWORD "qwerty1234"
#define MY_HOSTNAME "Boss1"

/** MQTT Configuration **/
#define MY_MQTT_PUBLISH_TOPIC_PREFIX "sendToPc/3"
#define MY_MQTT_SUBSCRIBE_TOPIC_PREFIX "getFromPc/3"
#define MY_MQTT_CLIENT_ID "Boss1"
#define MY_CONTROLLER_IP_ADDRESS 192, 168, 56, 101
#define MY_PORT 1883

/*******************************
* END MQTT CONFIG
********************************/
// MySensors radio defines

#define MY_NODE_ID TABLE_SECTION_ID



// Table section ID set node id between 1-254
#define TABLE_SECTION_ID 3

// ID of this I2C slave
#define SLAVE_ID 1

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
//#define FLOW_SEGMENT_COUNT 20

// For testing with one ledstrip in IPKW
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
