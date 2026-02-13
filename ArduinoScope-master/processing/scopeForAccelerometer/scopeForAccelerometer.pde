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
float AR[] = {0.0,0.0,0.0};
float ARalpha = 0.01;
float zoom;
byte lf = 10;
float alpha = 0.1;

long[] triggerTime = {0,0,0};
long[] prevTriggerTime = {0,0,0};
float[] topValue = {0.0, 0.0, 0.0};
float[] bottomValue = {0.0, 0.0, 0.0};
float[] amp = {0, 0, 0};
float[] freq = {0, 0, 0};

void setup() 
{
  size(640, 480);
  // Open the port that the board is connected to and use the same speed (9600 bps)
  println(Serial.list());
  port = new Serial(this, Serial.list()[portNumber], 115200);
  port.bufferUntil(lf);
  values = new float[3][width];
  //values = new float[3];
  zoom = 1.0f;
  smooth();
}

int getY(float val) {
  return (int)(((height/2) - val / 40.0f * (height))-1);
}

void serialEvent(Serial port) {
  String[] valuesString = split(port.readString(),",");
  if (valuesString.length ==3){
    pushValue(float(valuesString));
  }
  
}

//
void pushValue(float[] newValues) {
  //loop through dimensions
  for (int dim=0; dim<3; dim++){
    
    //shift all values in the screen buffer to make room for the new value
    for (int i=0; i<width-1; i++){
      values[dim][i] = values[dim][i+1];
    }
    //add new value at the end of the screen buffer 
    values[dim][width-1] = newValues[dim];
    
    //update long running averages
    AR[dim] = ((1 - ARalpha) * AR[dim]) + (ARalpha * newValues[dim]);

    //check for maximum or minimum value
    topValue[dim]=max(topValue[dim],newValues[dim]);
    bottomValue[dim]=min(bottomValue[dim],newValues[dim]);
    
    //if value crosses the AR[dim] line, we have had a full period and will calculate amplitude and frequency
    if ((values[dim][width-10] < AR[dim] ) & (newValues[dim] > AR[dim])){
      processTrigger(dim);
    }
  }
}

void processTrigger(int dim){
    prevTriggerTime[dim]=triggerTime[dim];
    triggerTime[dim]=millis();
    amp[dim] = ((1 - alpha) * amp[dim]) + (alpha * (topValue[dim]-bottomValue[dim]));
    
    float freqObs = 1000.0 / (triggerTime[dim] - prevTriggerTime[dim]);
    if (freqObs < 50.0){
      freq[dim] = ((1 - alpha) * freq[dim]) + (alpha * (freqObs));
    }
    topValue[dim]=AR[dim];
    bottomValue[dim]=AR[dim];
}




void drawLines() {
  stroke(255);
  
  int displayWidth = (int) (width / zoom);
  
  int k = values[0].length - displayWidth;
  
  int x0 = 0;
  int yX0 = getY(values[0][k]);
  int yY0 = getY(values[1][k]);
  int yZ0 = getY(values[2][k]);
  for (int i=1; i<displayWidth; i++) {
    k++;
    int x1 = (int) (i * (width-1) / (displayWidth-1));
    int yX1 = getY(values[0][k]);
    int yY1 = getY(values[1][k]);
    int yZ1 = getY(values[2][k]);
    stroke(255);
    line(x0, yX0, x1, yX1);
    stroke(255,0,0);
    line(x0, yY0, x1, yY1);
    stroke(0,255,0);
    line(x0, yZ0, x1, yZ1);
    x0 = x1;
    yX0 = yX1;
    yY0 = yY1;
    yZ0 = yZ1;
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
  text("A "+ nf(amp[0],1,2),10,32);
  text("F "+nf(freq[0],2,1),10,64);
  fill(255,0,0);
  text("A "+ nf(amp[1],1,2),150,32);
  text("F "+nf(freq[1],2,1),150,64);
  fill(0,255,0);
  text("A "+ nf(amp[2],1,2),300,32);
  text("F "+nf(freq[2],2,1),300,64);
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
