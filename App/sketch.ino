#include <Arduino.h>
#include <ESP32Servo.h>
#include <qrcodeoled.h>
#include <SSD1306.h>
#include "WiFi.h"

/* *********************************************************************************
 *        QRcode
 * dependency library :
 *   ESP8266 Oled Driver for SSD1306 display by Daniel Eichborn, Fabrice Weinberg
 *
 * SDA --> D6
 * SCL --> D7
***********************************************************************************/
#define OLEDDISPLAY


SSD1306  display(0x3c, 21, 22); // Only change
Servo servo;
QRcodeOled qrcode (&display);
const char* ssid = "Wokwi-GUEST";  
const char* pwd = "";
Servo arm; // Create a "Servo" object called "arm"
float pos = 0.0;
String TestLink = "https://youtu.be/dQw4w9WgXcQ?si=dyGIne3IyU0e8HT0"; 
bool opened=false;
// const char* ssid = "user2";  
// const char* pwd = "22222222";

void setup() {
  servo.attach(25,500, 2400);
  Serial.begin(115200);
  Serial.println("");
  // Serial.println("Starting...");
   Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, pwd, 6);
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
    Serial.print(".");
  }
  Serial.println(" Connected!");
  display.init();
  display.clear();
  display.display();
    Serial.println("clear...");

  // enable debug qrcode
  qrcode.debug();

  // Initialize QRcode display using library
  qrcode.init();
    Serial.println("init qr lib...");
  // create qrcode
  qrcode.create(TestLink);
  Serial.println("...");
}

void loop() {
  CloseOpen();
  delay(1000);
}
void CloseOpen(void){
  if(opened){
    servo.write(90);
    Serial.println("Open");
  }else{
    servo.write(0);
    Serial.println("Close");
  }
}
