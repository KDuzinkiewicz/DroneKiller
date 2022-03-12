import cv2
import numpy as np
import serial
import logging


ARDUINO_SERIAL_PORT = 'COM7'

# set root logger log level
logging.getLogger().setLevel(logging.INFO)

def main():
    logging.info('*** Serial Port Example ***')
    logging.info('Opening serial port...')
    # create a port (it will be atomatically opened upon creation)
    ser = serial.Serial(ARDUINO_SERIAL_PORT)
    if not ser.is_open:
        logging.error('Serial port not open.')
    logging.info('Serial port open.')


if __name__ == "__main__":
    main()