#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#define pinLock D2
//192.168.1.9
const uint16_t port = 65321;
const char *host = "192.168.43.222";
WiFiClient client;
char serverSignal;
unsigned long currentTime;
unsigned long preTime=5500;
bool isBuzz=false;
void setup()
{
    pinMode(pinLock,OUTPUT);
    Serial.begin(9600);
    Serial.println("");
    Serial.println("Connecting...\n");
    WiFi.mode(WIFI_STA);
    WiFi.begin("Ayaya", "12345687"); // change it to your ussid and password
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
     Serial.println("");
    Serial.println("Connected to wifi\n");
}

void loop()
{
  currentTime = millis();
    client.connect(host, port);
    delay(250);
    while (client.available() > 0)
    {
        serverSignal = client.read();
                if(serverSignal == '1')
                {
                  preTime = currentTime;
                }
                if(serverSignal == '2' && currentTime - preTime> 5000)
                {
                  Serial.print("Buzz");
                }
    }
    if(currentTime - preTime< 5000  ){
          Serial.print("Open");
          digitalWrite(pinLock,HIGH);
           delay(500);
      }else{
          Serial.print("Close");
          digitalWrite(pinLock,LOW);
           delay(500);
        }
    Serial.print('\n');
   
}
