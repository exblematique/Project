#include "config.h"
#include "load.h"
#include "voltage.h"

/* CURRENT TABLE RFID SETUP (AS SEEN FROM THE FRONT OF THE TABLE)
 * ************************************************************************************
 *        NORTH SIDE              
 *        
 *            T0                                          D33 
 *        M1       M2                                 D13       D27  
 *           \|_|/                                       \|_|/
 *      M0___/   \___M3              HELPER SIDE   D12___/   \___D12   BOSS SIDE
 *           \___/                                       \___/
 *           /| |\                                       /| |\
 *        M5       M4                                D27       D13
 *            T1                                          D33
 *            
 *        SOUTH SIDE    
 * ************************************************************************************   
 * M0/5 = MODULE_SENSORS
 * T0/1 = TABLE_SECTION_SENSORS
 * 
 * I/O Arduino pinout boss (as seen from the front of the table):
 * 
 * M4 = D13 (boss)
 * M3 = D12 (boss)
 * M2 = D27 (boss)
 * T0 = D33 (boss)
 *
 * M1 = D13 (helper)
 * M0 = D12 (helper)
 * M5 = D27 (helper)
 * T1 = D33 (helper)
 */

// initialization of table sensors and locations on the table 
const SensorInfo sensor_info[] = {
  [0] = { .type = MODULE_SENSOR,     .location = 4 }, //boss --digitalpin 13
  [1] = { .type = MODULE_SENSOR,     .location = 3 }, //boss --digitalpin 12
  [2] = { .type = MODULE_SENSOR,     .location = 2 }, //boss --digitalpin 27
  [3] = { .type = TABLE_SECTION_SENSOR, .location = 0 }, //boss --digitalpin 33
  [4] = { .type = MODULE_SENSOR,     .location = 1 }, //helper --digitalpin 13
  [5] = { .type = MODULE_SENSOR,     .location = 0 }, //helper --digitalpin 12
  [6] = { .type = MODULE_SENSOR,     .location = 5 }, //helper --digitalpin 27
  [7] = { .type = TABLE_SECTION_SENSOR, .location = 1 }, //helper --digitalpin 33
};

// initialization of RFID objects on the boss (helper RFIDs are send through I2C communication)
RFID RFIDs[RFID_COUNT] = {
  RFID_create(RFID0_SDA_PIN, RFID_RST_PIN),
  RFID_create(RFID1_SDA_PIN, RFID_RST_PIN),
  RFID_create(RFID2_SDA_PIN, RFID_RST_PIN),
  RFID_create(RFID3_SDA_PIN, RFID_RST_PIN),
};

// initialization of color settings with voltage being background color and load being foreground color
CRGB off_color = CRGB::Black;
CRGB error_color = CRGB::Red;
CRGB voltage_colors[] = {
  [VOLTAGE_LOW] = CRGB::Grey,
  [VOLTAGE_MEDIUM] = CRGB::DarkMagenta,
  [VOLTAGE_HIGH] = CRGB::DarkBlue,
};
CRGB load_colors[] = {
  [LOAD_NORMAL] = CRGB::Green,
  [LOAD_HIGH] = CRGB::Yellow,
  [LOAD_CRITICAL] = CRGB::Red,
};
