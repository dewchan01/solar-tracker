/*
 Web Client to consume Open WeatherMap web service
 
 This sketch connects to a website (http://api.openweathermap.org)
 using an Arduino Ethernet shield and get data from site.
 
 Circuit:
 * Arduino MEGA 2560 R3 Board
 * Ethernet shield attached to pins 10, 11, 12, 13
 
 created 24 May 2015
 by Erico Porto
 Based on the WeatherUnderground version from Afonso C. Turcato
 */

#include <ArduinoJson.h>
#include <SPI.h>
#include <Ethernet.h>
#include <UnixTime.h>

#define RBUFFSIZE 600

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
UnixTime stamp(8);//GMT+8
const char server[] = "api.openweathermap.org"; 

// Set the static IP address to use if the DHCP fails to assign
IPAddress ip(192,168,31,149);

EthernetClient client;

char responseBuffer[RBUFFSIZE];
int  rbindex = 0;

boolean startCapture;

void setup() {
  Serial.begin(9600);

  // start the Ethernet connection:
  if (Ethernet.begin(mac) == 0)
  {
    Serial.println("Failed to configure Ethernet using DHCP");
    Ethernet.begin(mac, ip);
  }
  
  // give the Ethernet shield a half-second to initialize:
  delay(500);
  Serial.print("My IP Address is: ");
  Serial.println(Ethernet.localIP());
  Serial.println("Connecting...");
  
  // if you get a connection, report back via serial:
  if (client.connect(server, 80))
  {
    Serial.println("Connected!");
    
    const String html_cmd1 = "GET /data/2.5/weather?q=Singapore,SG&appid=52264e8d49d86b8cfd40fb5fd86cab31";
    const String html_cmd2 = "Host: api.openweathermap.org";
    const String html_cmd3 = "Connection: close";
    
    //You can comment the following 3 lines 
    Serial.println(" " + html_cmd1);
    Serial.println(" " + html_cmd2);
    Serial.println(" " + html_cmd3);
    
    // Make a HTTP request:
    client.println(html_cmd1);
    client.println(html_cmd2);
    client.println(html_cmd3);
    client.println();
    
    responseBuffer[0] = '\0';
    rbindex = 0;

    startCapture = false;   
  } 
  else
  {
    // if you didn't get a connection to the server:
    Serial.println("Connection failed!");
  }
}

void loop()
{
  // if there are incoming bytes available 
  // from the server, read them and buffer:
  if (client.available())
  {
    char c = client.read();
    if(c == '{') {
      startCapture=true;
    }
    
    if(startCapture && rbindex < RBUFFSIZE) {
      responseBuffer[rbindex] = c;
      rbindex++;
    }
  }
  
  // if the server's disconnected, stop the client:
  if (!client.connected()) {   
      
    
    Serial.print("Received bytes");
    Serial.print(strlen(responseBuffer));
    Serial.println("Disconnecting.");
    client.stop();
    client.flush();
    
    Serial.println(responseBuffer);
    
    Serial.println();
        
    StaticJsonBuffer<500> jsonBuffer;
    
    JsonObject& root = jsonBuffer.parseObject(responseBuffer);

    if (!root.success()) {
      Serial.println("parseObject() failed");
    }  else {
      
        //String weatherId = root["weather"]["id"]; 
        String cityName = root["name"]; 
        double rain = root["rain"]["3h"];
        //double wind = root["wind"]["speed"];
        double maxtemperature = root["main"]["temp_max"]["metric"]; 
        double mintemperature = root["main"]["temp_min"]["metric"]; 
        String temp = String(lround((maxtemperature+mintemperature)/2));
        String humidity = root["main"]["humidity"]; 
        double cloud = root["clouds"]["all"];
        int visibility = root["visibility"];
        String weatherDesc = root["weather"]["description"];
        uint32_t sunRise = root["sys"]["sunrise"];
        uint32_t sunSet = root["sys"]["sunset"];
        String country = root["sys"]["country"];
        float longitude = root["coord"]["lon"];
        float latitude = root["coord"]["lat"];
        String lastUpdateTime = root["lastupdate"];

        
      //Now, some examples of how to use it!
      Serial.println("Current country: " + country);
      Serial.println("Current city: "+ cityName);
      Serial.println("Longitude: "+String(longitude));
      Serial.println("Latitude"+String(latitude));
      stamp.getDateTime(sunRise);
      Serial.println("Sun Rise Time: "+ String(stamp.hour) + ":" + String(stamp.minute) + ":" + String(stamp.second));
      stamp.getDateTime(sunSet);
      Serial.println("Sun Set time: "+ String(stamp.hour) + ":" + String(stamp.minute) + ":" + String(stamp.second));
      Serial.println("Max temperature: "+ String(maxtemperature) +" C");
      Serial.println("Min temperature: "+ String(mintemperature) +" C");
      Serial.println("Temperature: "+ temp + " C");
      Serial.println("Humidity: "+ humidity+ " %");
      Serial.println("Cloudiness "+ String(cloud) + " %");
      Serial.println("Visibility "+ String(visibility/1000)+ " km");
      Serial.println("Rain volume in last 3 hours: "+ String(rain) + " mm");  
      Serial.println("Weather: "+ weatherDesc);  
      Serial.println("Last updated on: "+ lastUpdateTime); 
    }
    delay(1000);
    // do nothing forevermore:
    //while(true);  
  }
}
