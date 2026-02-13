  /*
 * changes by Rolf Hut:
 * changed to only plot incoming serial data, works with the standard
 * AnalogReadSerial from the Arduino. 
 * However, the time axis becomes dependent on the size of the incomming 
 * serial string, so is slower 
  
  
 * Oscilloscope
 * Gives a visual rendering of analog pin 0 in realtime.
 * 
 * This project is part of Accrochages
 * See http://accrochages.drone.ws
 * 
 * (c) 2008 Sofian Audry (info@sofianaudry.com)
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */ 
import processing.serial.*;

int portNumber = 9; //which port to select. Run the 

Serial port;  // Create object from Serial class
float val;      // Data received from the serial port
float[][] values;
float AR[] = {1.0,1.0};
float ARalpha = 0.005;
float zoom;
byte lf = 10;
float alpha = 0.4;

long[] triggerTime = {0,0};
long[] prevTriggerTime = {0,0};
float[] topValue = {0.0, 0.0};
float[] bottomValue = {0.0, 0.0};
float[] amp = {0, 0};
float[] freq = {0, 0};

void setup() 
{
  size(640, 480);
  // Open the port that the board is connected to and use the same speed (9600 bps)
  println(Serial.list());
  port = new Serial(this, Serial.list()[portNumber], 115200);
  port.bufferUntil(lf);
  values = new float[2][width];
  //values = new float[3];
  zoom = 1.0f;
  smooth();
}

int getY(float val) {
  return (int)(((height/2) - (val - 9.81) / 40.0f * (height))-1);
}

void serialEvent(Serial port) {
  String[] valuesString = split(port.readString(),",");
  if (valuesString.length ==6){
    pushValue(float(valuesString));
  }
  
}

//
void pushValue(float[] newValues) {
  //loop through dimensions
  for (int sensor=0; sensor < 2; sensor++){
    float rmsNewValue = 0.0;
    for (int dim=0; dim<3; dim++){
      int readNr = dim * 2 + sensor;
      rmsNewValue = rmsNewValue + (newValues[readNr]*newValues[readNr]);
    }
    rmsNewValue = sqrt(rmsNewValue);
      
    //shift all values in the screen buffer to make room for the new value
    for (int i=0; i<width-1; i++){
      values[sensor][i] = values[sensor][i+1];
    }
    //add new value at the end of the screen buffer 
    values[sensor][width-1] = rmsNewValue;
    
    //update long running averages
    AR[sensor] = ((1 - ARalpha) * AR[sensor]) + (ARalpha * rmsNewValue);

    //check for maximum or minimum value
    topValue[sensor]=max(topValue[sensor],rmsNewValue);
    bottomValue[sensor]=min(bottomValue[sensor],rmsNewValue);
    
    //if value crosses the AR[dim] line, we have had a full period and will calculate amplitude and frequency
    if ((values[sensor][width-10] < AR[sensor] ) & (rmsNewValue > AR[sensor])){
      processTrigger(sensor);
    }
  }
}

void processTrigger(int sensor){
    prevTriggerTime[sensor]=triggerTime[sensor];
    triggerTime[sensor]=millis();
    amp[sensor] = ((1 - alpha) * amp[sensor]) + (alpha * (topValue[sensor]-bottomValue[sensor]));
    
    float freqObs = 1000 / (float)(triggerTime[sensor] - prevTriggerTime[sensor]);
    if (freqObs <20){
      freq[sensor] = ((1 - alpha) * freq[sensor]) + (alpha * (freqObs));
    }
    topValue[sensor]=AR[sensor];
    bottomValue[sensor]=AR[sensor];
}




void drawLines() {
  stroke(255);
  
  int displayWidth = (int) (width / zoom);
  
  int k = values[0].length - displayWidth;
  
  int x0 = 0;
  int y10 = getY(values[0][k]);
  int y20 = getY(values[1][k]);
  for (int i=1; i<displayWidth; i++) {
    k++;
    int x1 = (int) (i * (width-1) / (displayWidth-1));
    int y11 = getY(values[0][k]);
    int y21 = getY(values[1][k]);
    stroke(255,0,0);
    line(x0, y10, x1, y11);
    stroke(0,255,0);
    line(x0, y20, x1, y21);
    x0 = x1;
    y10 = y11;
    y20 = y21;
  }
}

void drawGrid() {
  stroke(255, 0, 0);
  //line(0, height/2, width, height/2);
  line(0, getY(AR[0]), width, getY(AR[0]));
  stroke(0,255,0);
  line(0, getY(AR[1]), width, getY(AR[1]));

}

void keyReleased() {
  switch (key) {
    case '+':
      zoom *= 2.0f;
      println(zoom);
      if ( (int) (width / zoom) <= 1 )
        zoom /= 2.0f;
      break;
    case '-':
      zoom /= 2.0f;
      if (zoom < 1.0f)
        zoom *= 2.0f;
      break;
    case 's':
      exit();
      break;
  }
}

void drawStats(){
  textSize(32);
  fill(255,0,0);
  text("A1 "+ nf(amp[0],1,2),10,32);
  text("F1 "+nf(freq[0],2,1),10,64);
  fill(0,255,0);
  text("A2 "+ nf(amp[1],1,2),10,420);
  text("F2 "+nf(freq[1],2,1),10,452);
}

void drawInfo(){
  textSize(16);
  fill(255);
  text("s: stop program \n+: zoom in (time)\n-: zoom out (time)",450,400);

}

void draw()
{
  background(0);
  drawGrid();
  drawLines();
  drawStats();
  drawInfo();
}
