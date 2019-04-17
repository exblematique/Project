#include "RFID.h"

/* ID of the I2C slave */
#define SLAVE_ID 1

/* Shared RFID reset pin */
#define RFID_RST_PIN A0

// RFID data pins 
#define RFID0_SDA_PIN 13
#define RFID1_SDA_PIN 12
#define RFID2_SDA_PIN 27
#define RFID3_SDA_PIN 33

/* Number of RFIDs on this Arduino */
#define RFID_COUNT 2

/* RFIDs on this Arduino */
extern RFID RFIDs[];
