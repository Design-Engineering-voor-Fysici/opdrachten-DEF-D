/*  
 HC-SR04 and HCSR05 Ping distance sensor
 This script outputs the duration of the pulse received from the
 sensor in microseconds.

 Works well with Processing program 'scopeForDistanceSensor' found at
 https://github.com/RolfHut/HC-SR04Tools

 Connection:
 VCC to arduino 5v 
 GND to arduino GND
 Echo to Arduino pin 6
 Trig to Arduino pin 5

 code by Rolf Hut, provided under Apache 2.0 License.
  */

#define trigPin 5
#define echoPin 6

void setup() {
  Serial.begin (9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(13, OUTPUT);
  digitalWrite(13,LOW);
}

void loop() {
  Serial.println(HCSR04Measurement(trigPin, echoPin,500));
  delay(100);
}

long HCSR04Measurement(int trigger, int echo, unsigned long timeout){
  digitalWrite(trigger, LOW);  
  delayMicroseconds(2); 
  digitalWrite(trigger, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigger, LOW);
  return pulseIn(echo, HIGH);
}
