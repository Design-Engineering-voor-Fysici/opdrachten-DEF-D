#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL343.h>

const float alpha = 0.1;
float x1 = 0.0;
float y1 = 0.0;
float z1 = 0.0;
float x2 = 0.0;
float y2 = 0.0;
float z2 = 0.0;

/* Assign a unique ID to the first sensor at the same time */
/* Uncomment following line for default Wire bus      */
/* and alternative I2C address 0X1D. Connect pin SDO  */
/* to Vcc for this. */
Adafruit_ADXL343 accel1 = Adafruit_ADXL343(12345);
Adafruit_ADXL343 accel2 = Adafruit_ADXL343(12346);




void setup(void)
{
  Serial.begin(115200);
  while (!Serial);
  Serial.println("Accelerometer Test"); Serial.println("");

  /* Initialise the sensors */
  if(!accel1.begin())
  {
    /* There was a problem detecting the ADXL343 ... check your connections */
    Serial.println("Ooops, no ADXL343 nr1 detected ... Check your wiring!");
    while(1);
  }
  if(!accel2.begin(0x1D))
  {
    /* There was a problem detecting the ADXL343 ... check your connections */
    Serial.println("Ooops, no ADXL343 nr2 detected ... Check your wiring!");
    while(1);
  }
  /* Set the range to whatever is appropriate for your project */
  accel1.setRange(ADXL343_RANGE_2_G);
  accel2.setRange(ADXL343_RANGE_2_G);

  /* Set the data rate to whatever is appropriate for your project */
  accel1.setDataRate(ADXL343_DATARATE_1600_HZ);
  accel2.setDataRate(ADXL343_DATARATE_1600_HZ);

  /* Display some basic information on this sensor */
  accel1.printSensorDetails();
  accel2.printSensorDetails();
  Serial.println("");
}

void loop(void)
{
  /* Get a new sensor event */
  sensors_event_t event1;
  sensors_event_t event2;
  accel1.getEvent(&event1);
  accel2.getEvent(&event2);

  /* Display the results (acceleration is measured in m/s^2) */
  x1 = ((1 - alpha) * x1 ) + (alpha * event1.acceleration.x);
  y1 = ((1 - alpha) * y1 ) + (alpha * event1.acceleration.y);
  z1 = ((1 - alpha) * z1 ) + (alpha * event1.acceleration.z);
  x2 = ((1 - alpha) * x2 ) + (alpha * event2.acceleration.x);
  y2 = ((1 - alpha) * y2 ) + (alpha * event2.acceleration.y);
  z2 = ((1 - alpha) * z2 ) + (alpha * event2.acceleration.z);
  Serial.print(x1); Serial.print(",");
  Serial.print(x2); Serial.print(",");
  Serial.print(y1); Serial.print(",");
  Serial.print(y2); Serial.print(",");
  Serial.print(z1); Serial.print(",");
  Serial.println(z2);
}
