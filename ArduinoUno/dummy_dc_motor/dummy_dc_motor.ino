#include <Adafruit_MotorShield.h>

// Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield();
// Or, create it with a different I2C address (say for stacking)
// Adafruit_MotorShield AFMS = Adafruit_MotorShield(0x61);

// Select which 'port' M1, M2, M3 or M4. In this case, M1
Adafruit_DCMotor *linearActuator1 = AFMS.getMotor(1);
Adafruit_DCMotor *linearActuator2 = AFMS.getMotor(2);

void setup() {
  // set LED pin
  pinMode(13, OUTPUT);

  if (AFMS.begin()) {
    // motor shield found

    // Set the speed to start, from 0 (off) to 255 (max speed)
    linearActuator1->setSpeed(255);
    linearActuator1->run(FORWARD);
    linearActuator2->setSpeed(255);
    linearActuator2->run(FORWARD);

    // turn on both motors
    linearActuator1->run(RELEASE);
    linearActuator2->run(RELEASE);
  }
  else {
    return;
  }
}

void loop() {
    // turn on both linear actuators for a brief time to pull the trigger
    // NOTE: Single linear actuator can draw up to 4A during startup so we need to make it quick
    linearActuator1->run(FORWARD);
    linearActuator2->run(FORWARD);
    delay(300);

    // turn off both linear actuators immediately not to burn the motor controller
    linearActuator1->run(RELEASE);
    linearActuator2->run(RELEASE);

    // let the motor controller to coo off
    delay(5000);

    // blink LED to indicate that we are not in reset state
    for (int i=0; i<3; i++) {
      digitalWrite(13, HIGH);
      delay(500);
      digitalWrite(13, LOW);
      delay(500);
    }
}
