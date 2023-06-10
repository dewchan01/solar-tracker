#define CAYENNE_PRINT Serial
#include <CayenneMQTTEthernet.h>    //CayenneMQTT library 
#include <Servo.h>                  //Servo motor library 
#include <DHT.h>                    //DHT library 
#define DHTTYPE DHT22
#define DHTPIN 2
DHT dht(DHTPIN, DHTTYPE);

#include <TimeLib.h>
//#include <LowPower.h>

#include <Wire.h>
#include <Adafruit_INA219.h>

//MQTT credentials
char username[] = "0fa09af0-1e3f-11ed-bf0a-bb4ba43bd3f6";
char password[] = "317896ff1bbcbb93c1b6454f16e5694a3916bcd4";
char clientID[] = "2795b910-1e3f-11ed-baf6-35fab7fd0ac8";

Servo servo_x;                   //up-down servomotor
int servoh = 0;
int servohLimitHigh = 170;
int servohLimitLow = 20;

Servo servo_z;                   //left-right servomotor
int servov = 0;
int servovLimitHigh = 170;
int servovLimitLow = 10;

int top, botl, botr;
int threshold_value = 10;
int LDRThreshold;
int servopos=0;
float current;
float voltage;
float power;
float Power_cell = 0;
float ETariff = 31.82;
int angle = 0;
int bearing = 0;
String orient;
String dir;
 
unsigned long timeNow = 0;
unsigned long timeLast = 0; //Time start Settings:
int startingHour = 6; // set your starting hour here, not below at int hour. This ensures accurate daily correction of time
int seconds = 19;
int minutes = 59;
int hours = startingHour;
int days = 0; //Accuracy settings
int dailyErrorFast = 0; // set the average number of milliseconds your microcontroller's time is fast on a daily basis
int dailyErrorBehind = 0; // set the average number of milliseconds your microcontroller's time is behind on a daily basis
int correctedToday = 1; // do not change this variable, one means that the time has already been corrected today for the error in your boards crystal. This is true for the first day because you just set the time when you uploaded the sketch.
int jfinal;

void setup()
{ Serial.begin(115200);
  /*while (!Serial){
    delay(1);
  }*/
  Cayenne.begin(username, password, clientID);
  servo_x.attach(5);
  servo_z.attach(6);
  dht.begin();
  pinMode(3, OUTPUT);
  digitalWrite(3, LOW);
 // if (! ina219.begin()){
   // Serial.println("Failed to find INA219 chip");
    /*while (1) {
      delay(10);
    }*/
  }
  //ina219.setCalibration_32V_1A();
//}

void loop()
{
  Cayenne.loop();
    
 voltage =  (18/5)* (analogRead(A4) * 5.0) / 1024;
   if (voltage<5 ){
      current= 0.30;}
  
  if (voltage>5 && voltage<=17.5){
      current= 0.29;}
      
  if(voltage >17.5){
      current=0.28;}
     
  power= voltage*current;

  
  Serial.print("Load Voltage:  "); Serial.print(voltage); Serial.println(" V");
  Serial.print("Current:       "); Serial.print(current); Serial.println(" A");
  Serial.print("Power:         "); Serial.print(power); Serial.println(" W");
  Serial.println("");

//searching for highest LDRThreshold
if (LDRThreshold==0){
    servov=170;
    servo_z.write(servov);
    servoh=20;
    servo_x.write(servoh);
    LDRThreshold=1;}

for(int i= 0;digitalRead(3) == HIGH;++i){
   
  top = analogRead(A0);
  botl = analogRead(A2);
  botr = analogRead(A3);
  
  Serial.print("top ");
  Serial.println(top);
  Serial.print("botr ");
  Serial.println(botr);
  Serial.print("botl ");
  Serial.println(botl);
  Serial.println();
 
    Serial.println("Automatic-mode");
    servoh = servo_x.read();
    servov = servo_z.read();
    int botavg = ((botr + botl) / 2);
    int avgright = (top + botr) / 2;
    int avgleft = (top + botl) / 2;
    int diffhori = avgright - avgleft;
    int diffverti = botavg - top;

    /*tracking according to vertical axis*/
    if (abs(diffverti) <= threshold_value)
    {
      servo_x.write(servoh);            //stop the servo up-down
    } 
    else {
      if (top>botavg+10)
      { 
        servo_x.write(servoh + 2);   //Clockwise rotation CW
        if (servoh > servohLimitHigh)
        {
          servoh = servohLimitHigh;
        }
      } 
      else if(top<botavg-10){
        servo_x.write(servoh - 2);  //CCW
        if (servoh < servohLimitLow)
        {
          servoh = servohLimitLow;
        }
      }
    }
    /*tracking according to horizontal axis*/
    if (abs(diffhori) <= threshold_value)
    {
      servo_z.write(servov);       //stop the servo left-right
    } 
    else {
      if (avgright<avgleft)
      {
          if (servoh<90)
        {servo_z.write(servov - 3);  }
        
          if (servoh>90)//clockwise
        {servo_z.write(servov + 3);   }
 
        if (servov > servovLimitHigh)
        {
          servov = servovLimitHigh;
        }
      } 
      else if (avgright>avgleft){
          if (servoh<90)
        {servo_z.write(servov + 3);  }
        
          if (servoh>90)//clockwise
        {servo_z.write(servov - 3);   }
          
        //delayMicroseconds(100);
        if (servov < servovLimitLow)
        {
          servov = servovLimitLow;
        }
      }
    }

    if(i== 1)
    break;
    //Calculate and display the current position of the solar panel 
if (servov > 90){
    bearing = servov - 90;
    if(servoh>90){bearing=bearing +180;}
    dir="E";
  }
if (servov == 90){
    bearing = 0;
    if(servoh>90){bearing=bearing +180;}
   dir="middle";
  }
if (servov < 90){
    bearing = servov+270;
    if(servoh>90){bearing=bearing -180;}
    dir= "W";
  }
if (servoh < 90){
    angle = servoh;
    orient = "N";
  }
if (servoh == 90){
    angle = 0;
    orient = "middle";
  }
if (servoh > 90){
    angle = 180 - servoh;
    orient = "S";
  } 
Serial.println(bearing, "bearing");
Serial.println(angle, "angle above horizontal");
  }
  Serial.println("Manual-mode");


timeNow = millis()/1000; // the number of milliseconds that have passed since boot
seconds = timeNow - timeLast;
//the number of seconds that have passed since the last time 60 seconds was reached.
if (seconds >= 60) {
timeLast = timeNow;
minutes = minutes + 1; 
seconds=0;}
//if one minute has passed, start counting milliseconds from zero again and add one minute to the clock.
if (minutes == 60){
minutes = 0;
hours = hours + 1; }
// if one hour has passed, start counting minutes from zero and add one hour to the clock
if (hours == 24){
hours = 0;
days = days + 1;
}
//if 24 hours have passed, add one day

if (hours ==(24 - startingHour) && correctedToday == 0){
delay(dailyErrorFast*1000);
seconds = seconds + dailyErrorBehind;
correctedToday = 1; }

if (hours==10 && minutes==0 && seconds==0){
    servov=170;
    servo_z.write(servov);
    servoh=20;
    servo_x.write(servoh);
}

//every time 24 hours have passed since the initial starting time and it has not been reset this day before, add milliseconds or delay the program with some milliseconds.
//Change these varialbes according to the error of your board.
// The only way to find out how far off your boards internal clock is, is by uploading this sketch at exactly the same time as the real time, letting it run for a few days
// and then determining how many seconds slow/fast your boards internal clock is on a daily average. (24 hours).
if (hours == 24 - startingHour + 2) {
correctedToday = 0; }
//let the sketch know that a new day has started for what concerns correction, if this line was not here the arduiono // would continue to correct for an entire hour that is 24 - startingHour.
Serial.print("The time is: ");
Serial.print(days);
Serial.print(":");
Serial.print(hours);
Serial.print(":");
Serial.print(minutes);
Serial.print(":");
Serial.println(seconds);
delay (100);

//Calculate and display the current position of the solar panel 
if (servov > 90){
    bearing = servov - 90;
    if(servoh>90){bearing=bearing +180;}
    dir="E";
  }
if (servov == 90){
    bearing = 0;
    if(servoh>90){bearing=bearing +180;}
   dir="middle";
  }
if (servov < 90){
    bearing = servov+270;
    if(servoh>90){bearing=bearing -180;}
    dir= "W";
  }
if (servoh < 90){
    angle = servoh;
    orient = "N";
  }
if (servoh == 90){
    angle = 0;
    orient = "middle";
  }
if (servoh > 90){
    angle = 180 - servoh;
    orient = "S";
  } 
Serial.println(bearing, "bearing");
Serial.println(angle, "angle above horizontal");
}

// Cayenne Functions
CAYENNE_IN(8) {
  int value = getValue.asInt();
  CAYENNE_LOG("Channel %d, pin %d, value %d", 8, 3, value);
  digitalWrite(3, value);
}
CAYENNE_IN(7) { //up-down servo motor
  if (digitalRead(3) == HIGH) { //Automatic_mode
    Cayenne.virtualWrite(7,servov);
  }
  else { //Manual_mode
    servo_x.write(getValue.asDouble()*180);
  }
}
CAYENNE_IN(6) { //left-right servo motor
  if (digitalRead(3) == HIGH) {
    Cayenne.virtualWrite(6,servoh);
  }
  else {
    servo_z.write(getValue.asDouble()*180);
  }
}
CAYENNE_OUT(18){//Power Gradient
  float temp = dht.readTemperature();

  
  if(int (temp)==23){ Power_cell=5.067;}
  if(int (temp)==24){ Power_cell=5.033;}
  if(int (temp)==25){ Power_cell=5.000;}
  if(int (temp)==26){ Power_cell=4.966;}
  if(int (temp)==27){ Power_cell=4.933;}
  if(int (temp)==28){ Power_cell=4.899;}
  if(int (temp)==29){ Power_cell=5.866;}
  if(int (temp)==30){ Power_cell=4.833;}
  if(int (temp)==31){ Power_cell=4.800;}
  if(int (temp)==32){ Power_cell=4.768;}
  if(int (temp)==33){ Power_cell=4.736;}
  if(int (temp)==34){ Power_cell=4.704;}
  
  
  Cayenne.virtualWrite(18, Power_cell ,"pow","w");
  
  
}
CAYENNE_OUT(0) { //Current
  float currentMeasured = current;
  Cayenne.virtualWrite(0, currentMeasured,"current","a");
  Serial.print("Current: ");
  Serial.println(currentMeasured);
}
CAYENNE_OUT(1) { //Voltage
  float voltageMeasured = voltage;
  Cayenne.virtualWrite(1, voltageMeasured,"voltage","v");
  Serial.print("Voltage: ");
  Serial.println(voltage);
}
CAYENNE_OUT(3) { //LDR Top
  Cayenne.virtualWrite(3, top);
}
CAYENNE_OUT(4) { //LDR Bot-left
  Cayenne.virtualWrite(4, botl);
}
CAYENNE_OUT(5) { //LDR Bot-right
  Cayenne.virtualWrite(5, botr);
}
CAYENNE_OUT(10) { //Power
  float powerMeasured = power;
  Cayenne.virtualWrite(10, powerMeasured,"pow","w");
  Serial.print("Power: ");
  Serial.println(power);
}
CAYENNE_OUT(11) { //Temperature
  float t = dht.readTemperature();
  //int chk = dht.read(DHT11PIN);
  Cayenne.virtualWrite(11, t, TYPE_TEMPERATURE, UNIT_CELSIUS);
  Serial.print("temperature: ");
  Serial.println(t);
}
CAYENNE_OUT(12) { //Humidity
  float h = dht.readHumidity();
  //int chk = dht.read(DHT11PIN);
  Cayenne.virtualWrite(12, h);
  Serial.print("  humidity: ");
  Serial.println(h);
}

CAYENNE_OUT(19){//Efficiency
  float perc = (power/Power_cell)*100;
  Cayenne.virtualWrite(19,perc,"lum","p");
}
CAYENNE_OUT(20){//Line Graph of calculated power cell and power observed
  Cayenne.virtualWrite(20,Power_cell,"pow","w");
  Cayenne.virtualWrite(20,(current*voltage),"pow","w");
}
CAYENNE_OUT(21){//Outcome profit
  float outcome = power/1000*ETariff;
  Cayenne.virtualWrite(21,outcome);
}
CAYENNE_OUT(22){//Current Electrical Tariff
  Cayenne.virtualWrite(22,ETariff);
}
CAYENNE_OUT(23){//Solar Panel Position bearing
    Cayenne.virtualWrite(23,bearing);

  }
CAYENNE_OUT(24){//Solar Panel Position angle
    Cayenne.virtualWrite(24,angle);
  }
CAYENNE_OUT(25){
    if (orient == "N"){
    Cayenne.virtualWrite(25,1,"digital_sensor", "d");
    }
    else{
    Cayenne.virtualWrite(25,0,"digital_sensor", "d");
    }
}
CAYENNE_OUT(26){
    if (orient == "S"){
    Cayenne.virtualWrite(26,1,"digital_sensor", "d");
    }
    else{
    Cayenne.virtualWrite(26,0,"digital_sensor", "d");
    }
}
CAYENNE_OUT(27){
    if (dir == "W"){
    Cayenne.virtualWrite(27,1,"digital_sensor", "d");
    }
    else{
    Cayenne.virtualWrite(27,0,"digital_sensor", "d");
    }
} 
CAYENNE_OUT(28){
    if (dir == "E"){
    Cayenne.virtualWrite(28,1,"digital_sensor", "d");
    }
    else{
    Cayenne.virtualWrite(28,0,"digital_sensor", "d");
    }
} 
CAYENNE_OUT(29){
    if (orient == "middle"){
    Cayenne.virtualWrite(29,1,"digital_sensor", "d");
    }
    else{
    Cayenne.virtualWrite(29,0,"digital_sensor", "d");
    }
} 
CAYENNE_OUT(30){
    if (dir == "middle"){
    Cayenne.virtualWrite(30,1,"digital_sensor", "d");
    }
    else{
    Cayenne.virtualWrite(30,0,"digital_sensor", "d");
    }
} 
