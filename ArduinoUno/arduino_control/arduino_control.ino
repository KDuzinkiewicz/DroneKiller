#include <Adafruit_MotorShield.h>

// Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield();
// Or, create it with a different I2C address (say for stacking)
// Adafruit_MotorShield AFMS = Adafruit_MotorShield(0x61);

// Select which 'port' M1, M2, M3 or M4. In this case, M1
Adafruit_DCMotor *linearActuator1 = AFMS.getMotor(1); // 1st linear actuator for trigger control
Adafruit_DCMotor *linearActuator2 = AFMS.getMotor(2); // 2nd linear actuator for trigger control
Adafruit_DCMotor *motorX = AFMS.getMotor(3); // DC motor for moving in the X axis
Adafruit_DCMotor *motorY = AFMS.getMotor(4); // DC motor for moving in the Y axis

void pull_trigger() {
    // turn on both linear actuators for a brief time to pull the trigger
    // NOTE: Single linear actuator can draw up to 4A during startup so we need to make it quick
    linearActuator1->run(FORWARD);
    linearActuator2->run(FORWARD);
    delay(300);

    // turn off both linear actuators immediately not to burn the motor controller
    linearActuator1->run(RELEASE);
    linearActuator2->run(RELEASE);
}


void setup() {
    // set LED pin
    pinMode(13, OUTPUT);

    // configure DC motors
    if (AFMS.begin()) {
        // motor shield found

        //set the speed to start, from 0 (off) to 255 (max speed)
        linearActuator1->setSpeed(255);
        linearActuator1->run(FORWARD);
        linearActuator2->setSpeed(255);
        linearActuator2->run(FORWARD);
        motorX->setSpeed(255);
        motorX->run(FORWARD);
        motorY->setSpeed(255);
        motorY->run(FORWARD);

        // turn on all motors
        linearActuator1->run(RELEASE);
        linearActuator2->run(RELEASE);
        motorX->run(RELEASE);
        motorY->run(RELEASE);
    }
    else {
        return;
    }

    // configure serial port
    // set up Serial library at 9600 bps
    Serial.begin(9600);
}

void loop() {
    // pull the trigger
    pull_trigger();

    // let the motor controller to cool off
    delay(5000);

    // blink LED to indicate that we are not in reset state
    for (int i=0; i<3; i++) {
      digitalWrite(13, HIGH);
      delay(500);
      digitalWrite(13, LOW);
      delay(500);
    }
}
