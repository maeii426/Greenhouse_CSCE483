#include "LowPower.h"
#include "RF24.h"
#include "RF24Network.h"
#include "RF24Mesh.h"
#include <SPI.h>
#include <EEPROM.h>
#include "RF24Mesh_Config.h"

#define SOILSENSOR     0      // Soil Moisture Sensor - Start @ A0 (sequential)
#define POWERPINSTART  2      // Start of the power pins, starting at D2 (sequential)
#define NUM_OF_SENSORS 1      // Define the # of sensors connected starting from Pin A0
#define CONFIG_START   0      // Location of stored config data
#define RF_POWER_PIN   9      // RF24 Power Pin on Arduino - D9

/**** Configure the nrf24l01 CE and CS pins ****/
RF24 radio(7, 8);
RF24Network network(radio);
RF24Mesh mesh(radio, network);

/**
 * User Configuration: nodeID - A unique identifier for each radio. Allows addressing
 * to change dynamically with physical changes to the mesh.
 *
 * A unique value from 1-255 must be configured for each node.
 * This will be stored in EEPROM, so it remains persistent between further uploads, loss of power, etc.
 *
 **/
 
uint16_t sleep_counter = 0;
uint8_t pwr_pins[NUM_OF_SENSORS]; // Array of the digital pins used to power the moisture sensors

struct Configuration {
  uint16_t nodeID;                 // Unique NodeID used in the RF24 Mesh Network
  uint16_t nodeFamily;            // NodeFamily to increase sensors beyond 255
  char program_version[4];        // Determining the version of our settings
} settings = {
  // Default Values
  NODEID,
  NODEFAMILY,
  CONFIG_VERSION
};

/*
 * Types
 * 0 - SOIL
 * 1 - HYDROPONICS
 */

struct payload_t {
  uint32_t sensorID;// 4-bytes unsigned INT - plantID of sensor
  uint8_t  type;    // 1-byte unsigned INT - Type of data
  uint32_t moisture; // 4-byte unsigned INT - moisture
  uint16_t wtemp;
  uint16_t humid; 
};

payload_t payload;

// Set the power pins to be OUTPUT and turned off
void initialize() {
  int i;
  for (i = 0; i < NUM_OF_SENSORS; i++) {
    pwr_pins[i] = POWERPINSTART + i;
    pinMode(pwr_pins[i], OUTPUT);
    digitalWrite(pwr_pins[i], LOW);
  }
}

// Verify they are our desired settings
void loadConfig() {
  if (EEPROM.read(CONFIG_START + sizeof(settings) - 2) == CONFIG_VERSION[2] &&
      EEPROM.read(CONFIG_START + sizeof(settings) - 3) == CONFIG_VERSION[1] &&
      EEPROM.read(CONFIG_START + sizeof(settings) - 4) == CONFIG_VERSION[0]) 
  {
    for (unsigned int i = 0; i < sizeof(settings); i++) {
      *((char*)&settings + i) = EEPROM.read(CONFIG_START + i);
    }
  } else {
    // Settings are not valid - overwrite with default settings
    Serial.println("Writing new defualt settings into EEPROM.");
    saveConfig();
  }
}

void saveConfig() {
  for (unsigned int i = 0; i < sizeof(settings); i++) {
    EEPROM.write(CONFIG_START + i, *((char*)&settings + i));
    if (EEPROM.read(CONFIG_START + i) != *((char*)&settings + i)) {
      Serial.println("ERROR WRITING TO EEPROM");
    }
  }
}

void setup() {
  pinMode(RF_POWER_PIN, OUTPUT);
  digitalWrite(RF_POWER_PIN, HIGH); // Turn it on immediately
  Serial.begin(115200);
  loadConfig();
  mesh.setNodeID(settings.nodeID);
  initialize();
  if (settings.nodeID == 0) settings.nodeID = 1;
  payload.sensorID = settings.nodeFamily * 255 + settings.nodeID;
  payload.type = 0;
  Serial.println(payload.sensorID);

  // Connect to the mesh
  Serial.println(F("Connecting to the mesh..."));
  mesh.begin(MESH_DEFAULT_CHANNEL, RF24_250KBPS, MESH_RENEWAL_TIMEOUT);
}

void loop() {
  radio.powerUp();
  sleep_counter += 8;
  if (sleep_counter>=SLEEP_INTERVAL) {
    mesh.renewAddress(60000);
    mesh.update();
    int i;
    for (i = 0; i < NUM_OF_SENSORS; i++) {
      digitalWrite(pwr_pins[i], HIGH);
      delay(50); // Small delay to ensure moisture reads correctly
      int moisture = analogRead(SOILSENSOR+i);
      if (moisture == 0)
        moisture = 1050;

      digitalWrite(pwr_pins[i], LOW);
      payload.moisture = moisture;

      // Send an 'M' (master) type message with the moisture reading
      if (!mesh.write(&payload, 'M', sizeof(payload))) {
        delay(2000);  // Sleep for 2 seconds before trying to connect again
        // If a write fails, check connectivity to the mesh network
        if (!mesh.checkConnection() ) {
          Serial.println("Renewing Address");
          mesh.renewAddress();
        } else {
          Serial.println("Send fail, Test OK");
        }
      } else Serial.print("Send OK");
    }
    sleep_counter=0; // Reset sleep counter
  }
  mesh.releaseAddress();
  radio.powerDown();
  LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
}


