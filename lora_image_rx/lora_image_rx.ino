/*
 * 2020-08-07 / 2020-08-08 NOI Hackathon Summer Edition
 * Team WANted Bytes
 * 
 * LoRa Image RX Module
 * Arduino Uno WiFi v2 + Dragino LoRa Shield v95
 */

#include <SPI.h>
#include <LoRa.h>

/*
 * By changing the spreading factor (FS), multiple LoRa devices can communicate at the
 * same time, on the same frequency, without causing corrupted packets (signals on different
 * SF are orthogonal to each other). We use this characteristic to allow multiple LoRa transceivers
 * to send different parts of the same image at the same time, increasing the total throughput.
 */
#define SPREADING_FACTOR 8
// In our experiment, we used SF 8 and 9

char packet[256];

void setup() {
  Serial.begin(115200);
  while (!Serial);

  //Serial.println("LoRa Receiver");

  if (!LoRa.begin(868E6)) {
    Serial.println("Starting LoRa failed!");
    
    while (1);
  }
  LoRa.enableCrc();
  LoRa.setSpreadingFactor(SPREADING_FACTOR);
}

void loop() {
  
  int packetSize = LoRa.parsePacket();
  // If a new packet has been received:
  if (packetSize) {

    //Serial.print("Received packet '");

    // Read packet
    int i = 0;
    int offset = -4;
    bool isValid = true;
    while (LoRa.available()) {
      char c = (char)LoRa.read();
      if (i + offset >= 0) {
        //packet[i + offset] = c;
        Serial.print(c);
      }
      if (i < 4 && c != '!') {
        isValid = false;
      }
      i++;
    }

    // Kind of a hack, necessary before sending the ACK to allow the other transceiver to switch back to RX mode (I guess, not completely sure though)
    delay(50);
    // Send the ACK
    sendLoRa("!");
  }
}

void sendLoRa(char* text){

  LoRa.beginPacket();
  LoRa.print(text);
  LoRa.endPacket();
}
