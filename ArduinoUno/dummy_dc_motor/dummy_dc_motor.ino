#include <Adafruit_MotorShield.h>

// Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield();
// Or, create it with a different I2C address (say for stacking)
// Adafruit_MotorShield AFMS = Adafruit_MotorShield(0x61);

// Select which 'port' M1, M2, M3 or M4. In this case, M1
Adafruit_DCMotor *myMotor = AFMS.getMotor(1);
// You can also make another motor on port M2
//Adafruit_DCMotor *myOtherMotor = AFMS.getMotor(2);


void setup() {
  if (AFMS.begin()) {
    // motor shield found
    pinMode(13, OUTPUT);
    digitalWrite(13, HIGH);

    // Set the speed to start, from 0 (off) to 255 (max speed)
    myMotor->setSpeed(255);
    myMotor->run(FORWARD);
    // turn on motor
    //myMotor->run(RELEASE);
  }
}

void loop() {
    // myMotor->run(FORWARD);
    // delay(1000);


//   digitalWrite(13, HIGH);
//   delay(1000);
//   digitalWrite(13, LOW);
//   delay(500);
}
