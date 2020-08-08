/*
 * 2020-08-07 / 2020-08-08 NOI Hackathon Summer Edition
 * Team WANted Bytes
 * 
 * LoRa Image TX Module
 * Seeeduino LoRaWAN v1.0
 */

#include <SPI.h>
#include <LoRaWan.h>

#define SPREADING_FACTOR SF8

String preamble = "!!!!";
String text = "empty";
unsigned char buffer[128] = {0, };
char bufferTx[260] = {0, };

//void sendLoRa(String text);

void setup() {

  bufferTx[0] = '!';
  bufferTx[1] = '!';
  bufferTx[2] = '!';
  bufferTx[3] = '!';
  
  Serial.begin(115200);
  while (!Serial);

  //Serial.println("LoRa Sender");

  lora.init();
  lora.initP2PMode(868, SPREADING_FACTOR, BW125, 8, 8, 20);
}

int packetSize;
bool packet_sent;
void loop() {

  if (Serial.available() > 0) {
    // text = Serial.readStringUntil('\n');
    int txLen = 4;
    while (Serial.available()) {
      char c = Serial.read();
      if (c == '\n') break;
      bufferTx[txLen] = c;
      txLen++;
    }
    bufferTx[txLen] = '\0';
    //Serial.println(bufferTx);
    lora.transferPacketP2PMode(bufferTx, txLen);

    packet_sent = false;
    while (!packet_sent){
      //Serial.println('.');
      short length = 0;
      short rssi = 0;
   
      memset(buffer, 0, 128);
      length = lora.receivePacketP2PMode(buffer, 128, &rssi, 1);
      //Serial.println(length);
   
      if(length)
      {

        for(unsigned char i = 0; i < length; i ++)
        {
          SerialUSB.print((char)buffer[i]);
        }
        packet_sent = true;
      }
    }
  }
}
