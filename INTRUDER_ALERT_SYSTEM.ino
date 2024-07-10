#include <Arduino.h>
#include <SoftwareSerial.h>
#include "HX711.h">

// HX711 circuit wiring
const int LOADCELL_DOUT_PIN = 2;
const int LOADCELL_SCK_PIN = 3;
#define Calibration_factor 10
HX711 scale;

int reading;
int lastReading;


const int IR_Pin = 7;
const int GLED_Pin = 11;
const int RLED_Pin = 12;
const int SPEAKER_Pin = 13;  // Speaker pin
const int GSM_RX_Pin = 8;    // Connect GSM TX to Arduino pin 8
const int GSM_TX_Pin = 9;    // Connect GSM RX to Arduino pin 9
int i = 0;

SoftwareSerial gsmSerial(GSM_RX_Pin, GSM_TX_Pin);

void setup() {
  Serial.begin(57600);    // Serial monitor for debugging
  gsmSerial.begin(9600);  // Initialize GSM module
  Serial.println("Initializing the scale");
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);

  scale.set_scale(Calibration_factor);
  scale.tare();

  pinMode(IR_Pin, INPUT);
  pinMode(GLED_Pin, OUTPUT);
  pinMode(RLED_Pin, OUTPUT);
  pinMode(SPEAKER_Pin, OUTPUT);  // Speaker pin as output

  // Initialize LEDs to an off state
  digitalWrite(GLED_Pin, HIGH);
  digitalWrite(RLED_Pin, LOW);
}

void loop() {

  if (scale.wait_ready_timeout(200)) {
    reading = abs(round(scale.get_units()));
    Serial.print("Weight: ");
    Serial.println(reading);
    // if (reading != lastReading) {
    //   displayWeight(reading);
    // }
    lastReading = reading;
  } else {
    Serial.println("HX711 not found.");
  }


  int IR_State = digitalRead(IR_Pin);

  if (IR_State == LOW && reading > 100) {
    digitalWrite(GLED_Pin, LOW);   // Green LED on
    digitalWrite(RLED_Pin, HIGH);  // Red LED off
    Serial.println("Intruder detected!");
    sendToGSM("+254726339318", "Intruder detected!");  // Replace +1234567890 with the recipient's phone number
    Serial.println("Activating buzzer...");
    digitalWrite(SPEAKER_Pin, HIGH);  // Power up the speaker (buzzer)
    delay(100);                       // Buzzer on for 1 second
    digitalWrite(SPEAKER_Pin, LOW);   // Turn off the speaker (buzzer)
  } else if (IR_State == HIGH) {
    digitalWrite(GLED_Pin, HIGH);  // Green LED off
    digitalWrite(RLED_Pin, LOW);   // Red LED on
    Serial.println("All clear");
    sendToGSM("+254726339318", "All clear");  // Replace +1234567890 with the recipient's phone number
  } else if (IR_State == LOW && reading < 100) {
    digitalWrite(GLED_Pin, LOW);  // Green LED on
    digitalWrite(RLED_Pin, HIGH);
    Serial.println("FALSE ALARM !!!!");
    sendToGSM("+254726339318", "FALSE ALARM !!!!!");
  }

  delay(100);  // Reduced delay for smoother operation
}

void sendToGSM(String phoneNumber, String message) {
  gsmSerial.println("AT");  // Send AT command to check if GSM module is responding
  delay(100);               // Wait for the response
  while (gsmSerial.available()) {
    Serial.write(gsmSerial.read());  // Print response to serial monitor
  }

  gsmSerial.println("AT+CMGF=1");  // Set SMS mode to text
  delay(100);                      // Wait for the response
  while (gsmSerial.available()) {
    Serial.write(gsmSerial.read());  // Print response to serial monitor
  }

  gsmSerial.print("AT+CMGS=\"");
  gsmSerial.print(phoneNumber);
  gsmSerial.println("\"");
  delay(100);  // Wait for the response
  while (gsmSerial.available()) {
    Serial.write(gsmSerial.read());  // Print response to serial monitor
  }

  gsmSerial.print(message);
  delay(100);
  gsmSerial.write(0x1A);  // End SMS transmission
  delay(100);             // Delay to ensure complete message transmission
}
