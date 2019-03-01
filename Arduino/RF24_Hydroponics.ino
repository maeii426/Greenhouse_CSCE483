#include "LowPower.h"
#include "RF24.h"
#include "RF24Network.h"
#include "RF24Mesh.h"
#include <SoftwareSerial.h>
#include <SPI.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#define PH_RX              2      // PH Sensor RX pin
#define PH_TX              3      // PH Sensor TX pin
#define POWER_PIN          4      // PH Sensor Power Pin
#define PHSENSOR_ID        47     // Should be changed in the future for further scalability

#define WATERLVL_POWER_PIN 2      // Turn on/off the water level sensor to avoid corrosion
#define RF_POWER_PIN       9      // RF24 Power Pin on Arduino - D9
#define CONFIG_START       0      // Location of stored config data
#define SLEEP_INTERVAL     10     // Readings every X*8 seconds

#define ONE_WIRE_BUS 5        // Data wire in D5 on Arduino
#define WATERLVL     0        // Waterlevel sensor in A0

SoftwareSerial myserial(PH_RX, PH_TX); 

OneWire oneWire(ONE_WIRE_BUS);

DallasTemperature sensors(&oneWire);

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

byte received_from_sensor = 0;
uint32_t ph = 0;
byte string_received = 0;
char ph_data[20];

/*
 * Types
 * 0 - SOIL
 * 1 - HYDROPONICS
 */

struct payload_t {
  uint32_t sensorID;// 4-bytes unsigned INT - plantID of sensor
  uint8_t  type;    // 1-byte unsigned INT - Type of data
  uint32_t moisture; // 4-byte moisture
  uint16_t wtemp; // 2-byte water temp
};

payload_t payload;

void setup() {
  pinMode(POWER_PIN, OUTPUT);
  pinMode(WATERLVL_POWER_PIN, OUTPUT);
  pinMode(RF_POWER_PIN, OUTPUT);
  digitalWrite(RF_POWER_PIN, HIGH);
  Serial.begin(115200);
  myserial.begin(38400);
  mesh.setNodeID(PHSENSOR_ID);
  payload.sensorID = PHSENSOR_ID;
  payload.type = 1;
  Serial.println(payload.sensorID);
  digitalWrite(WATERLVL_POWER_PIN, LOW);
  sensors.begin();

  // Connect to the mesh
  Serial.println(F("Connecting to the mesh..."));
  mesh.begin(MESH_DEFAULT_CHANNEL, RF24_250KBPS, MESH_RENEWAL_TIMEOUT);
}

void loop() {
  radio.powerUp();
  sleep_counter++;
  if (sleep_counter==(SLEEP_INTERVAL/8)) {
    mesh.renewAddress(60000);
    mesh.update();
    digitalWrite(WATERLVL_POWER_PIN, HIGH);
    sensors.requestTemperatures();
    payload.wtemp = (int)sensors.getTempCByIndex(0);
    float pH = 0.0;
    payload.moisture = analogRead(WATERLVL);
    digitalWrite(WATERLVL_POWER_PIN, LOW);
 
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
    sleep_counter=0; // Reset sleep counter
  }
  mesh.releaseAddress();
  radio.powerDown();
  LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
}


