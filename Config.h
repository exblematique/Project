#ifndef CONFIG_H
#define CONFIG_H

#include <FastLED.h>

#include "rfid.h"
#include "sensor-info.h"

// Enable the MY_DEBUG define to show debug messages
#define MY_DEBUG


/**************************************
* Ethernet Gateway Transport Defaults
* To use network, use the library <Ethernet.h>
***************************************/
#define MY_GATEWAY_ESP32

/** Configuration of WiFi */
#define MY_WIFI_SSID "MySSID"
#define MY_WIFI_PASSWORD "MyVerySecretPassword"

/** Static IP/MAC address. If not defined, DHCP will be used */
#define MY_HOSTNAME "Boss1"
#define MY_IP_ADDRESS 192,168,1,1
#define MY_MAC_ADDRESS 0xDE,0xAD,0xBE,0xEF,0xFE,0x01

/** IP/subnet of gateway. If not defined, DHCP will be used
#define MY_IP_GATEWAY_ADDRESS 192,168,1,254
#define MY_IP_SUBNET_ADDRESS 255,255,255,0
#define MY_PORT 5003	//Port open in gateway
*/


//#define MY_DEBUG_VERBOSE_GATEWAY	//Verbose debug prints related to the gateway transport
/**
 * @def MY_PORT
 * @brief The Ethernet TCP/UDP port to open on controller or gateway.
 */
//#ifndef MY_PORT
//#ifdef MY_GATEWAY_MQTT_CLIENT
//#define MY_PORT 1883
//#else
//#define MY_PORT 5003
//#endif
//#endif

/**
 * @def MY_MQTT_CLIENT_PUBLISH_RETAIN
 * @brief Enables MQTT client to set the retain flag when publishing specific messages.
 */
//#define MY_MQTT_CLIENT_PUBLISH_RETAIN
/**
 * @def MY_MQTT_PASSWORD
 * @brief Used for authenticated MQTT connections.
 *
 * Set if your MQTT broker requires username/password.
 * Example: @code #define MY_MQTT_PASSWORD "secretpassword" @endcode
 * @see MY_MQTT_USER
 */
//#define MY_MQTT_PASSWORD "secretpassword"
//#define MY_MQTT_USER "username"
/**
 * @def MY_MQTT_CLIENT_ID
 * @brief Set client ID for MQTT connections
 *
 * This define is mandatory for all MQTT client gateways.
 * Example: @code #define MY_MQTT_CLIENT_ID "mysensors-1" @endcode
 */
//#define MY_MQTT_CLIENT_ID "mysensors-1"
/**
 * @def MY_MQTT_PUBLISH_TOPIC_PREFIX
 * @brief Set prefix for MQTT topic to publish to.
 *
 * This define is mandatory for all MQTT client gateways.
 * Example: @code #define MY_MQTT_PUBLISH_TOPIC_PREFIX "mygateway1-out" @endcode
 */
//#define MY_MQTT_PUBLISH_TOPIC_PREFIX "mygateway1-out"
/**
 * @def MY_MQTT_SUBSCRIBE_TOPIC_PREFIX
 * @brief Set prefix for MQTT topic to subscribe to.
 *
 * This define is mandatory for all MQTT client gateways.
 * Example: @code #define MY_MQTT_SUBSCRIBE_TOPIC_PREFIX "mygateway1-in" @endcode
 */
//#define MY_MQTT_SUBSCRIBE_TOPIC_PREFIX "mygateway1-in"


/**
 * @def MY_IP_RENEWAL_INTERVAL_MS
 * @brief DHCP, default renewal setting in milliseconds.
 */
//#ifndef MY_IP_RENEWAL_INTERVAL_MS
//#define MY_IP_RENEWAL_INTERVAL_MS (60*1000ul)
//#endif

/**
 * @def MY_CONTROLLER_IP_ADDRESS
 * @brief If this is defined, gateway will act as a client trying to contact controller on
 *        @ref MY_PORT using this IP address.
 * If left un-defined, gateway acts as server allowing incoming connections.
 */
//#define MY_CONTROLLER_IP_ADDRESS 192,168,178,254

/**
 * @def MY_CONTROLLER_URL_ADDRESS
 * @brief If this is defined, gateway will act as a client (ethernet or MQTT) trying to
 *        contact controller on the given URL.
 */
//#define MY_CONTROLLER_URL_ADDRESS "test.mosquitto.org"


/***********************************
 *	The rest of original software
 ***********************************/
// Table section ID set node id between 1-254
#define TABLE_SECTION_ID 4

// ID of this I2C slave
#define SLAVE_ID 1

// Shared RFID reset pin
#define RFID_RST_PIN A0

// RFID data pins 
#define RFID0_SDA_PIN 5
#define RFID1_SDA_PIN 6
#define RFID2_SDA_PIN 7
#define RFID3_SDA_PIN 8

// Number of RFIDs on this Arduino
#define RFID_COUNT 4

// Delay in ms between RFID checks
#define RFID_CHECK_DELAY 75

// Led strip data pin
#define LEDSTRIP_DATA_PIN 3

// Led strip clock pin
#define LEDSTRIP_CLK_PIN 2

// Led strip type with clock pin (currently SK9822 is used, not APA102 even though it says on the label because of chinese clone manufacturers)
#define LEDSTRIP_TYPE SK9822

// Number of flow_segments
#define FLOW_SEGMENT_COUNT 20

// Number of LEDs in each flow_segment
#define FLOW_SEGMENT_LENGTH 6

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