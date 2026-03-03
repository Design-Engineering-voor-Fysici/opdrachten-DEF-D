/*  
 HC-SR04 and HCSR05 Ping distance sensor
 This script outputs the distance measured by the HC-SR04 sensor. Needs calibration constants!
 Calibration constant provided with this script are nonsense! This is because my students need to add
 their own calibration constants!

 Works well with Processing program 'scopeForDistanceSensor' found at
 https://github.com/RolfHut/HC-SR04Tools

 Connection:
 VCC to arduino 5v 
 GND to arduino GND
 Echo to Arduino pin 6
 Trig to Arduino pin 5

 code by Rolf Hut, provided under Apache 2.0 License.
  */

#include "math.h"

//the pin definitions:
#define trigPin 5
#define echoPin 6

//the calibration constants
#define alpha 0.0347
#define beta -1.0

void setup() {
  Serial.begin (9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {

  long duration = HCSR04Measurement(trigPin, echoPin);
  
  //different options for calculating distance from duration. Remove the // from the line you want to use.
  
  //linear
  float distance = (alpha * duration) + beta;

  //power law
  //float distance = alpha * (pow(duration,beta));

  //exponential
  //float distance = alpha * exp(duration * beta);

  //only print results if within 0 to 200 cm.
  if (not(distance >= 200 || distance <= 0)){
    Serial.println(distance);
  }
  delay(50);
}


long HCSR04Measurement(int trigger, int echo){
  digitalWrite(trigger, LOW);  
  delayMicroseconds(2); 
  digitalWrite(trigger, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigger, LOW);
  return pulseIn(echo, HIGH);
}
