from turtle import delay
import cv2
import numpy as np
import serial
import logging
import time

ARDUINO_SERIAL_PORT = 'COM7'


# set root logger log level
logging.getLogger().setLevel(logging.INFO)


def main():
    logging.info('*** Serial Port Example ***')
    logging.info(f'Opening serial port: {ARDUINO_SERIAL_PORT}...')
    # create a port (it will be automatically opened upon creation)
    arduino_serial_port = serial.Serial(ARDUINO_SERIAL_PORT)
    if not arduino_serial_port.is_open:
        logging.error('Serial port not open.')
    logging.info('Serial port open.')

    for i in range(5):
        # write a few simple commands via serial port to control Arduino
        logging.info('Turning LED on...')
        arduino_serial_port.write(b"LED_ON")
        time.sleep(2)
        logging.info('Turning LED off...')
        arduino_serial_port.write(b"LED_OFF")
        time.sleep(2)

    logging.info('DONE')


if __name__ == "__main__":
    main()
