  /*
 * program to check which ports are available on your machine. 
 */
import processing.serial.*;

Serial port;  // Create object from Serial class

void setup() 
{
  //size(1280, 480);
  // Open the port that the board is connected to and use the same speed (9600 bps)
  for(int i=0;i<Serial.list().length;i++){
    println(str(i) + " " + Serial.list()[i]);
  }
}


void draw()
{
}
