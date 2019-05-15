/*
 * Smart Grid TableController handles messages received by Smart Grid MainController
 * It displays a simulation of the electrical grid between consumers and producers  
 * 
 * The TableController sends messages to the MainController when a module/other table is placed.
 * The MainController receives these messages and does the calculation of the simulation. 
 * When the calculation is done, the MainController sends the grid/flow configuration back and the TableController shows the simulation
 * 
 * For configurations see config.h
 * 
 * Created by: Joris van Zeeland, Jelle Bouwhuis, Kevin Taartmans, Sam Teuwsen, Willem van der Krol, Derk Wiegerinck
 * Contact: jorisvanzeeland@hotmail.com
 * Date: July 11th, 2017
 * Commisioned by: Dr. Ballard Asare-Bediako, Dhr. Eddy Luursema 
 * Location: HAN University of Applied Sciences - Arnhem
 */

#include "config.h"

#include <MySensors.h>

#include "ledstrip.h"
#include "grid.h"
#include "protocol.h"
#include "rfid.h"
#include "synced-millis.h"

//present tablesection to maincontroller
void presentation() {
  present(TABLE_SECTION_ID, S_CUSTOM);
}

void setup()
{
  /* start Serials:
   *  Serial is used to print something in the serial monitor
   *  Serial2 is used to receive a piece of information from ESP helper
   */
  Serial.begin(BAUDRATE);
  Serial2.begin(BAUDRATE, SERIAL_8N1, RX_PIN, TX_PIN);
  
  // start SPI for RFID readers
  SPI.begin();

  // initialize RFID readers 
  for (size_t i = 0; i < RFID_COUNT; i++)
  {
    RFID_init(&RFIDs[i]);
  }

  // initialize led strips
  ledstrip_setup();

  //Set RST pin on helper high default status
  pinMode(HELPER_RST_PIN, OUTPUT);
  digitalWrite(HELPER_RST_PIN, LOW);
  delay(5);
  digitalWrite(HELPER_RST_PIN, HIGH);

} // End setup()

void loop()
{
  // handle an RFID message on this ESP32
  for (int i=0; i<RFID_COUNT; i++){
    handle_RFID(&RFIDs[i], i);
  }

  /* handle an RFID message received by serial:
   *    Receives the first byte which contain the sensor_id (config.cpp for more information)
   *    The receives the second byte for the tag_present
   *    The lasts bytes it's for the tag_id which is a 4-bytes value
   */
  if (Serial2.available()){
    noInterrupts();
    RFID_message RFID_msg;
    RFID_msg.sensor_id = Serial2.read() + RFID_COUNT;
    RFID_msg.tag_present = (bool) Serial2.read();
    
    if (RFID_msg.tag_present){
      for (int i=0; i<4; i++){
        RFID_msg.tag_id = (RFID_msg.tag_id >> 8) | (Serial2.read() << 24);
      } 
    }
    interrupts();
    handle_RFID_message(&RFID_msg);
  }
  
  ledstrip_update();
} // End loop()

// Handles incoming message from main-controller. This is a built-in function from the MySensors library
void receive(const MyMessage &msg)
{
  // if TEST_MODULE is placed don't receive messages
  if (ledstrip_test(testReady)) {
    return;
  }

  // Check if it needs a reboot
  if (msg.type == REBOOT_BOSS_AND_HELPER_MSG) {
    Serial.println("Reboot command received from maincontroller");
    reboot_boss_and_helper();
  }

  // Check if there is an update for the flow_segment configuration
  if (msg.type == FLOW_CONFIG_CHANGE_MSG)
  {
    Grid grid = grid_from_parsed_grid((const ParsedGrid*) msg.getCustom());

    ledstrip_set_grid(&grid);

    // Force led strip update
    ledstrip_update(true);

#ifdef MY_DEBUG
    // If debugging is enabled, this will print the energy grid (grid) info
    grid_print(&grid);
#endif

  }
  // Check if there is a color change message 
  else if (msg.type == COLOR_CHANGE_MSG)
  {
    // convert string to RGB value
     char rgbHex[7];
    msg.getString(rgbHex);
    rgbHex[6] = '\0';

    uint32_t rgb = strtoul(rgbHex, NULL, 16);

    ledstrip_set_color(msg.sensor, rgb);

    // force led strip update
    ledstrip_update(true);
  }
  // Check if there is a time synchronization message (for cross-table segments flow_segment synchronization)
  else if (msg.type == TIME_SYNC_MSG)
  {
    set_millis(msg.getULong());
  }


} // End receive()

// Handles RFID tag detection from boss
void handle_RFID(RFID *RFID, uint8_t sensor_id)
{
  // Jump out of the function if the RFID state has not changed
  if (!RFID_state_changed(RFID))
  {
    return;
  }

  // create RFID message
  RFID_message msg = {
    .sensor_id = sensor_id,
    .tag_present = RFID->tag_present,
  };

  // read tag ID if a tag is present
  if (msg.tag_present)
  {
    bool tag_id_read = RFID_start_auth(RFID) &&
                       RFID_tag_read_id(RFID, &msg);

    RFID_stop_auth(RFID);
        
    // Jump out of the function if the tag can't be read properly
    if (!tag_id_read)
    {
      return;
    }
  }
  handle_RFID_message(&msg);
} // End handle_RFID()

// Processes the incoming RFID message
void handle_RFID_message(const RFID_message *msg)
{
  #ifdef MY_DEBUG
    // If debugging is enabled, this prints the RFID message
    RFID_message_print(msg);
  #endif

  // report change to main controller
  const SensorInfo *sensor = &sensor_info[msg->sensor_id];

  if (sensor->type == MODULE_SENSOR)
  {
    uint32_t module_id = msg->tag_present ? msg->tag_id : 0;

    change_module(sensor->location, module_id);
  }
  else // If the sensor type is not a module sensor, it must be a table detection sensor
  {
    uint32_t table_section_id = msg->tag_present ? msg->tag_id : 0;

    change_neighbor(sensor->location, table_section_id);
  }

   // if TEST_MODULE is placed execute ledstrip_test
    if (msg->tag_id == TEST_MODULE_ID && msg->tag_present == true)
    {
      Serial.println("Test module is placed");
      testReady = false;
      testReady = ledstrip_test(testReady);
    }
} // End handle_RFID_message()

void reboot_boss_and_helper() {
  Serial.println("rebooting system");
  ESP.restart();
  //wait for it to reboot
} 
