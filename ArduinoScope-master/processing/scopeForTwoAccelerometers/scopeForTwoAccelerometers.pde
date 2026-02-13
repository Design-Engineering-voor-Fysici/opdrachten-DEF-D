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
float AR[] = {0.0,0.0,0.0,0.0,0.0,0.0};
float ARalpha = 0.01;
float zoom;
byte lf = 10;
float alpha = 0.1;

long[] triggerTime = {0,0,0,0,0,0};
long[] prevTriggerTime = {0,0,0,0,0,0};
float[] topValue = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
float[] bottomValue = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
float[] amp = {0, 0, 0, 0, 0, 0};
float[] freq = {0, 0, 0, 0, 0, 0};

void setup() 
{
  size(640, 480);
  // Open the port that the board is connected to and use the same speed (9600 bps)
  println(Serial.list());
  port = new Serial(this, Serial.list()[portNumber], 115200);
  port.bufferUntil(lf);
  values = new float[6][width];
  //values = new float[3];
  zoom = 1.0f;
  smooth();
}

int getY(float val) {
  return (int)(((height/2) - val / 40.0f * (height))-1);
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
  for (int dim=0; dim<3; dim++){
    for (int sensor=0; sensor < 2; sensor++){
      int readNr = dim * 2 + sensor; 
      //shift all values in the screen buffer to make room for the new value
      for (int i=0; i<width-1; i++){
        values[readNr][i] = values[readNr][i+1];
      }
      //add new value at the end of the screen buffer 
      values[readNr][width-1] = newValues[readNr];
      
      //update long running averages
      AR[readNr] = ((1 - ARalpha) * AR[readNr]) + (ARalpha * newValues[readNr]);
  
      //check for maximum or minimum value
      topValue[readNr]=max(topValue[readNr],newValues[readNr]);
      bottomValue[readNr]=min(bottomValue[readNr],newValues[readNr]);
      
      //if value crosses the AR[dim] line, we have had a full period and will calculate amplitude and frequency
      if ((values[readNr][width-10] < AR[readNr] ) & (newValues[readNr] > AR[readNr])){
        processTrigger(dim, sensor);
      }
    }
  }
}

void processTrigger(int dim, int sensor){
  int readNr = dim * 2 + sensor;
    prevTriggerTime[readNr]=triggerTime[readNr];
    triggerTime[readNr]=millis();
    amp[readNr] = ((1 - alpha) * amp[readNr]) + (alpha * (topValue[readNr]-bottomValue[readNr]));
    
    float freqObs = 1000.0 / (triggerTime[readNr] - prevTriggerTime[readNr]);
    if (freqObs < 50.0){
      freq[readNr] = ((1 - alpha) * freq[readNr]) + (alpha * (freqObs));
    }
    topValue[readNr]=AR[readNr];
    bottomValue[readNr]=AR[readNr];
}




void drawLines() {
  stroke(255);
  
  int displayWidth = (int) (width / zoom);
  
  int k = values[0].length - displayWidth;
  
  int x0 = 0;
  int yX10 = getY(values[0][k]);
  int yY10 = getY(values[2][k]);
  int yZ10 = getY(values[4][k]);
  int yX20 = getY(values[1][k]);
  int yY20 = getY(values[3][k]);
  int yZ20 = getY(values[5][k]);
  for (int i=1; i<displayWidth; i++) {
    k++;
    int x1 = (int) (i * (width-1) / (displayWidth-1));
    int yX11 = getY(values[0][k]);
    int yY11 = getY(values[2][k]);
    int yZ11 = getY(values[4][k]);
    int yX21 = getY(values[1][k]);
    int yY21 = getY(values[3][k]);
    int yZ21 = getY(values[5][k]);
    stroke(255);
    line(x0, yX10, x1, yX11);
    line(x0, yX20, x1, yX21);
    stroke(255,0,0);
    line(x0, yY10, x1, yY11);
    line(x0, yY20, x1, yY21);
    stroke(0,255,0);
    line(x0, yZ10, x1, yZ11);
    line(x0, yZ20, x1, yZ21);
    x0 = x1;
    yX10 = yX11;
    yY10 = yY11;
    yZ10 = yZ11;
    yX20 = yX21;
    yY20 = yY21;
    yZ20 = yZ21;
  }
}

void drawGrid() {
  stroke(255, 0, 0);
  line(0, height/2, width, height/2);
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
  fill(255);
  text("A1 "+ nf(amp[0],1,2),10,32);
  text("F1 "+nf(freq[0],2,1),10,64);
  fill(255,0,0);
  text("A1 "+ nf(amp[1],1,2),150,32);
  text("F1 "+nf(freq[1],2,1),150,64);
  fill(0,255,0);
  text("A1 "+ nf(amp[2],1,2),300,32);
  text("F1 "+nf(freq[2],2,1),300,64);
  fill(255);
  text("A2 "+ nf(amp[3],1,2),10,420);
  text("F2 "+nf(freq[3],2,1),10,452);
  fill(255,0,0);
  text("A2 "+ nf(amp[4],1,2),150,420);
  text("F2 "+nf(freq[4],2,1),150,452);
  fill(0,255,0);
  text("A2 "+ nf(amp[5],1,2),300,420);
  text("F2 "+nf(freq[5],2,1),300,452);
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
