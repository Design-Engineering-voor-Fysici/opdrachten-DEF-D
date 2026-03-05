/*Capacitance measurement circuit for Cx, from 0.1pF to 100nF without range switching
stable readout resolution is around 4 digits, resulting in:
0.1pF up to 1nF
1pF up to 10nF
10pF up to 100nF
Circuit uses only 2 current limiting resistors and 1 external reference capacitor Cref
*/

//  Connections:
byte Cx_PIN1 = A3;  // define Cx pin 1 connection (via 220 ohm series resistor from Arduino pin)
byte Cx_PIN2 = A0;  // define Cx pin 2 connection (via 220 ohm series resistor from Arduino pin)
// Cref sets the scale and is connected between Cx pin 2 and GND (ground)
// Resistors are limiting max currents and enable readout of large capacitor values for Cx >10nF 

//  Variables:
float Cx = 0;  //Measured and calculated capacitance value between Cx_PIN1 and Cx_PIN2
// To improve the stability of the measurement, a certain amount of readings is averaged:
int SumCnt = 0;  //sum counter, how many readings are currently taken and summed up
int SumCntmax = 1250;  //sum counter max value (1250 readings takes 180 milliseconds, time measured via scope)
float SumVal = 0;  // Summed reading results
float AvgVal = 0;  // Average value = SumVal/SumCnt

const int ADCmax = 1023;  // max value for the ADC, used as the fullscale value

// Calibration values for Cref and offset:
const float Cref_extern = 1000;  // added external capacitor Cref, in pF
const float Cin_Arduino = 23.1;  // estimated input capacitance Arduino, in pF 
const float Cref  = Cin_Arduino + Cref_extern;  // calculate Cref total, in pF
const float C_offset = 0.4;  // offset adjust, in pF


void setup(){  // initialise pins and communication:
  pinMode(Cx_PIN1, OUTPUT);  // this pin is a logic output driving Cx PIN1
  digitalWrite(Cx_PIN1, LOW);
  pinMode(Cx_PIN2, OUTPUT);  // this pin is later toggled between output and input mode, now start with output mode
  digitalWrite(Cx_PIN2, LOW);  // when in output mode, this pin is LOW
  Serial.begin(56700);  // define baudrate of communication to PC, set serial monitor readout to this value 
}

void loop(){
 SumCnt = 0;  //clear counter for number of readings
 SumVal = 0;  //clear sum value of reading results

 while (SumCnt<SumCntmax){  // Start of summing up readings loop
   pinMode(Cx_PIN2, INPUT);  // switch Cx_PIN2 mode to input mode for doing analog reading
   digitalWrite(Cx_PIN1, HIGH);  // switch Cx_PIN1 to high level
   SumVal=SumVal + analogRead(Cx_PIN2);  // measure voltage and add to sum
   
   //  Now discharge both Cx and Cref capacitors for next measurement:
   digitalWrite(Cx_PIN1, LOW);  // switch Cx_PIN1 to LOW for doing discharge
   pinMode(Cx_PIN2, OUTPUT);  // switch Cx_PIN2 mode to output mode (LOW) for doing discharge
   SumCnt = SumCnt + 1;  // increase counter value
 }  // end of summing up readings loop

 AvgVal = SumVal / SumCntmax;  // calculate average value: divide sum by number of readings

// Calculate capacitor value if ADC not in overload:
if (AvgVal<ADCmax){  // if readout not in overload, calculate and send result
  float Cx = (AvgVal * Cref) / (float)(ADCmax - AvgVal) -C_offset;
  //  Send result to PC via USB comport: 
  Serial.print(Cx, 1);  // send Cx value, 1 digit behind the comma (giving 0.1pF resolution)
  Serial.print(" pF ");  // print text: pF 
  Serial.println(" ");  //send linefeed to start new line
}
// If ADC in overload, also happens when having short circuit in Cx, send warning
else{Serial.println("OVERLOAD / SHORT CIRCUIT");}

//  Wait untill exactly 200milliseconds have passed and start again:
while (millis() % 200 != 0);    
}
