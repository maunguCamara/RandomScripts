#include <SoftwareSerial.h>

SoftwareSerial sim900(7, 8); //RX, TX pins connected to SIM900
const int greenLED = 10; //connect green LED to pin 10
const int redLED = 11; // red led to pin 11

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600); //start serial communication
  sim900.begin(9600); // start SIM900 module communication
  delay(3000);
  sim900.println("AT");
  delay(1000);
  pinMode(greenLED, OUTPUT);
  pinMode(redLED, OUTPUT);
  while (sim900.available()) {
    Serial.write(sim900.read());
  }
}

void sendSMS(String phoneNumber, String message) {
  sim900.println("AT+CMGF=1"); //Set SMS mode to text mode
  delay(100);
  sim900.println("AT+CMGS=\"" + phoneNumber + "\""); //set recipient phone number
  delay(100);
  sim900.print(message); //send message
  delay(100);
  sim900.write(26); //ASCII code for Ctrl+Z (end of message)
  delay(100);
}

void loop() {
  // put your main code here, to run repeatedly
    if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "GREEN") {
      digitalWrite(greenLED, HIGH);
      delay(500);
      digitalWrite(greenLED, LOW);
    } else if (command == "RED") {
      digitalWrite(redLED, HIGH);
      delay(500);
      digitalWrite(redLED, LOW);
    } else if (command == "OFF") {
      digitalWrite(greenLED, LOW);
      digitalWrite(redLED, LOW);
    } else if (command == "SEND_SMS") {
      sendSMS("+254703678264", "Unauthorized access detected!");  // Replace with recipient phone number
    }
    else if (command == "ALREADY_CHECKED_IN"){
      sendSMS("+254703678264", "You have already checked in");
    }
    else if (command == "APPEARED_ON_LIST"){
      sendSMS("+254703678264", "Face appears on  the list");
    }
    
    }
  }
  

