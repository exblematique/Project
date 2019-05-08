#include "RFID.h"

/* Serial Pins */
#define BAUDRATE 115200
#define TX_PIN 17
#define RX_PIN 16

/* Shared RFID reset pin */
#define RFID_RST_PIN A0

// RFID data pins 
#define RFID0_SDA_PIN 13
#define RFID1_SDA_PIN 12 //12
#define RFID2_SDA_PIN 27
#define RFID3_SDA_PIN 33

/* Number of RFIDs on this Arduino */
#define RFID_COUNT 4

/* RFIDs on this Arduino */
extern RFID RFIDs[];
