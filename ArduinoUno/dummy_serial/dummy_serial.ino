void setup() {
  // set LED pin
  pinMode(13, OUTPUT);

  // set up Serial library at 9600 bps
  Serial.begin(9600);
}

void loop() {
    // read command from serial port
    String command = Serial.readString();
    if (command != "") {
        // send the command back
        Serial.println(command);
    }

    if (command == "LED_ON") {
      digitalWrite(13, HIGH);
    }
    else if (command == "LED_OFF") {
      digitalWrite(13, LOW);
    }
}
