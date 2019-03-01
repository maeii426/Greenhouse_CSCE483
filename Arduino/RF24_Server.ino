#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>

// Serial prints out with a baudrate of 115200
// Typical values is that around <~500 means it is moist, and >~500 is not too moist.
#include "RF24.h"
#include "RF24Network.h"
#include "RF24Mesh.h"
#include <SPI.h>
#include <EEPROM.h>

#define SOIL      0
#define HYDRO     1

#define LIGHT_PIN A0
#define DHTTYPE   DHT22 // DHT 22 (AM2302)
#define DHTPIN   2
#define GREENHOUSEID 2

/**** Configure the NRF24L01 CE and CS pins ****/
RF24 radio(7, 8);
RF24Network network(radio);
RF24Mesh mesh(radio, network);

/**    Create the United DHT Sensor object **/
DHT_Unified dht(DHTPIN, DHTTYPE);

/**
 * User Configuration: 
 *   nodeID - Must be set to 00 for Master Node (Server)
 *
 **/
uint16_t nodeID = 00;
unsigned long lastReading;
unsigned long interval = 15000;
//unsigned long interval = 15000000; // 15 minute intervals

uint16_t lightReading;


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

void setup() {
  Serial.begin(9600);
  dht.begin();
  sensor_t sensor;
  dht.temperature().getSensor(&sensor);
  dht.humidity().getSensor(&sensor);
  lastReading = millis();
  mesh.setNodeID(nodeID);
 
  // Connect to the mesh
  mesh.begin(MESH_DEFAULT_CHANNEL, RF24_250KBPS, MESH_RENEWAL_TIMEOUT);
}

void loop() {
  if (millis() - lastReading > interval) {
    lightReading = analogRead(LIGHT_PIN);
    sensors_event_t event;
    int temp;
    int humid;
    dht.temperature().getEvent(&event);
    temp = (int)event.temperature;
    dht.humidity().getEvent(&event);
    humid = (int)event.relative_humidity;
    if (!isnan(temp) && !isnan(humid) && temp > 0 && humid > 0) {
      lastReading = millis();
      char buf[100];
      const char *mask = "GLOBAL:%d:%d:%d:%d\n";
      sprintf(buf, mask, GREENHOUSEID, lightReading, temp, humid);
      Serial.write(buf);
    }
  }
  mesh.update();
  mesh.DHCP();
  while (network.available()) {
    char buf[100];
    RF24NetworkHeader header;
    network.peek(header);
    payload_t payload;
    switch(header.type) {
      case 'M': {
                // Write to Serial in the form 'sensorID:Moisture'
                network.read(header, &payload, sizeof(payload));
                const char mask[100];
                if (payload.type == SOIL) {
                  // Write to Serial in form 'SOIL:sensorID:moisture'
                  strcpy(mask, "SOIL:%lu:%d");
                  sprintf(buf, mask, (unsigned long)payload.sensorID, payload.moisture);
                } else if (payload.type == HYDRO) {
                  // Write to Serial in the form 'HYDRO:sensorID:PH:WaterTemp:WaterLVL'
                  strcpy(mask, "HYDRO:%lu:0.0:%d:%d");
                  sprintf(buf, mask, (unsigned long)payload.sensorID, payload.wtemp, payload.moisture);
                }
                Serial.println(buf); // Send to the serial which is read by the RPi
                break;
      }
      default:  network.read(header, 0, 0);
                Serial.print("Rcv bad type ");
                Serial.print(header.type);
                Serial.print(" from 0");
                Serial.println(header.from_node);
                break;
    }
  }
  delay(2);
}
