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

// command received over serial port
String command = "";


void parse_and_execute_command(String command) {

    if (command == "TRG") {
        Serial.println("FIRE!!!");
        // pull_trigger();
    }
    else if (command == "GUN_ON") {
        Serial.println("Turn on gun motor");
        gun_on();
    }
    else if (command == "GUN_OFF") {
        Serial.println("Turn off gun motor");
        gun_off();
    }
    else {
        String tmp = command.substring(0, command.indexOf("_"));

        if (tmp == "DC") {
            Serial.println("Motor control");

            String tmp2 = command.substring(command.indexOf("_") + 1);
            String motor_speed_x_str = tmp2.substring(0, tmp2.indexOf("_"));
            String motor_speed_y_str = tmp2.substring(tmp2.indexOf("_") + 1);

            Serial.println(motor_speed_x_str);
            Serial.println(motor_speed_y_str);

            // motor control command
            int motor_speed_x = motor_speed_x_str.toInt();
            int motor_speed_y = motor_speed_y_str.toInt();
        }
        else {
            Serial.println("CMD unknown");
        }

        // other commands are not supported
    }

    return;
}


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


void gun_on() {
    // TODO: add code here
}


void gun_off() {
    // TODO: add code here
}


void setup() {
    // set LED pin
    pinMode(13, OUTPUT);

    // // configure DC motors
    // if (AFMS.begin()) {
    //     // motor shield found

    //     //set the speed to start, from 0 (off) to 255 (max speed)
    //     linearActuator1->setSpeed(255);
    //     linearActuator1->run(FORWARD);
    //     linearActuator2->setSpeed(255);
    //     linearActuator2->run(FORWARD);
    //     motorX->setSpeed(255);
    //     motorX->run(FORWARD);
    //     motorY->setSpeed(255);
    //     motorY->run(FORWARD);

    //     // turn on all motors
    //     linearActuator1->run(RELEASE);
    //     linearActuator2->run(RELEASE);
    //     motorX->run(RELEASE);
    //     motorY->run(RELEASE);
    // }
    // else {
    //     return;
    // }

    // configure serial port
    // set up Serial library at 9600 bps
    Serial.begin(9600);
}

void loop() {

    if (Serial.available()) {

        // read a single character from serial port
        char c = Serial.read();

        if (c == '\n') {
            Serial.println("CMD received");
            Serial.println(command);
            parse_and_execute_command(command);
            command = "";

            // signal receiving of the command
            digitalWrite(13, HIGH);
            delay(500);
            digitalWrite(13, LOW);
            delay(500);
        }
        else {
            command += c;
        }
    }

    // TODO: Support other commands
}
