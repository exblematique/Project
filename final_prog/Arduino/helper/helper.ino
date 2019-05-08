#include <SPI.h>

#include "config.h"

void setup()
{
	/* start SPI for RFID readers */
	SPI.begin();

	/* initialize RFID readers */
	for (size_t i = 0; i < RFID_COUNT; i++) {
		RFID_init(&RFIDs[i]);
	}
 
  /* start Serial communications (USB then ESP32 boss */
  Serial.begin(BAUDRATE);
  Serial2.begin(BAUDRATE, SERIAL_8N1, RX_PIN, TX_PIN);
	Serial.println("setup() finished");
}

void loop()
{
	for (size_t i = 0; i < RFID_COUNT; i++) {
		handle_RFID(&RFIDs[i], i);
	}
}

void handle_RFID(RFID *RFID, uint8_t sensor_id)
{
	/* skip RFID if state has not changed */
	if (!RFID_state_changed(RFID)) {
		return;
	}

	/* create RFID message */
	RFID_message msg = {
		.sensor_id = sensor_id,
		.tag_present = RFID->tag_present,
	};

	/* read tag ID if tag is present */
	if (msg.tag_present) {
		bool tag_id_read = RFID_start_auth(RFID) &&
		                   RFID_tag_read_id(RFID, &msg);

		RFID_stop_auth(RFID);

		/* ignore RFID if tag ID could not be read */
		if (!tag_id_read) {
			return;
		}
	}

	handle_RFID_message(&msg);
}

void handle_RFID_message(const RFID_message *msg)
{
	/* print RFID message */
	RFID_message_print(msg);
  
	/* send RFID message to serial */
  if (msg->tag_present) {
    byte buf[6];
    buf[0] = msg->sensor_id;
    buf[1] = (byte) msg->tag_present;
    for (int i=0; i<4; i++){
      buf[i+2] = (msg->tag_id >> i*8) & 255;
    }
    Serial2.write(buf, sizeof(buf));
  }
  else {
    byte buf[2];
    buf[0] = msg->sensor_id;
    buf[1] = (byte) msg->tag_present;
    Serial2.write(buf, sizeof(buf));  
  }
}
