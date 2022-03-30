import argparse
import cv2
import cv2.aruco as aruco
import logging
import time
import serial
import argparse
import numpy as np


ARDUINO_SERIAL_PORT = 'COM7'


# set root logger log level
logging.getLogger().setLevel(logging.INFO)


def send_motor_x_y_speed(arduino_serial_port, motor_speed_x, motor_speed_y):
    '''
    Send command over serial to Arduino to set the X & Y DC motor speed
    '''

    arduino_serial_port.write(bytearray(f'DC_{motor_speed_x}_{motor_speed_y}'))


def send_gun_on(arduino_serial_port):
    '''
    Send command over serial to Arduino to turn on the gun motor
    '''

    arduino_serial_port.write(b'GUN_ON')


def send_gun_off(arduino_serial_port):
    '''
    Send command over serial to Arduino to turn off the gun motor
    '''

    arduino_serial_port.write(b'GUN_OFF')


def send_pull_trigger(arduino_serial_port):
    '''
    Send command over serial to Arduino to pull the trigger
    '''

    arduino_serial_port.write(b'TRG')


def get_camera_width_height(camera_idx):
    '''
    Gets camera's image frame width and height

    Parameters:
        camera_idx (int): camera index

    Returns:
        width, height (int)
    '''

    video_capture = cv2.VideoCapture(camera_idx, cv2.CAP_DSHOW)
    if not video_capture.read()[0]:
        logging.warning(f'Invalid camera index')
        video_capture.release()
        return None
    else:
        logging.info(f'Camera idx {camera_idx} available')
        width = video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        logging.info(f'Camera idx {camera_idx} width: {width}, height: {height}')
        video_capture.release()
        return width, height


def get_cameras(max_idx=10):
    '''
    Gets a dictionary of camera indices and image parameters (width and height)

    Parameters:
        max_idx (int): up to what camera index to enumerate

    Returns:
        cameras (dict): key = camera index, value = tuple: camera's image frame width and height
    '''

    logging.info('Enumerating cameras...')

    cameras = {}

    for i in range(max_idx + 1):
        logging.info(f'Analyzing camera idex: {i}/{max_idx}...')
        result = get_camera_width_height(i)
        if result is not None:
            cameras[i] = result

    return cameras


def load_ar_image(path):
    img = cv2.imread(path)
    w, h = img.shape[0:2][::-1]
    corners = np.array([[0, 0], [w, 0], [w, h], [0, h]]).astype(int)
    return img, w, h, corners


def load_friendly():
    return load_ar_image('PC/images/friendly.png')


def load_foe():
    return load_ar_image('PC/images/foe.png')


def calculate_motor_speed(error, deadzone, min_motor_speed, max_motor_speed, k):
    '''
    Calculates motor speed in range [min_motor_speed, max_motor_speed] or zero if th error is within deadzone

    Parameters:
        error (int): error in pixels
        deadzone (int): deadzone in pixels
        min_motor_speed (int): Arduino motor shield PWM setting in range of [0, 255] at which the motor starts moving
        max_motor_speed (int): Arduino motor shield PWM setting in range of [0, 255] which we consider maximum allowable speed
        k (float): proportional constant between error in pixels and PWM value

    Returns:
        motor_speed (int): Arduino motor shield PWM setting in range of [-255, 255]
        NOTE: user will need to check for motor speed sign to set proper motor direction using Arduino library
    '''

    assert min_motor_speed < max_motor_speed, 'Min. motor speed has to be smaller than max. speed'
    assert type(min_motor_speed) is int
    assert type(max_motor_speed) is int
    assert min_motor_speed >= 0
    assert max_motor_speed <= 255

    if abs(error) <= deadzone:
        return 0

    # calculate desired motor speed to eliminate the error (simple P-control)
    # NOTE: The + and - pins of the DC motor need to be connected accordingly to be aligned with positive and
    # negative error in the pixel domain
    motor_speed = k * error

    if abs(motor_speed) > max_motor_speed:
        return max_motor_speed if error > 0 else -max_motor_speed

    if abs(motor_speed) < min_motor_speed:
        return min_motor_speed if error > 0 else -min_motor_speed

    return motor_speed


def main():

    # ArUco marker IDs legend
    FOE_ID = 0
    FRIENDLY_ID = 1

    # deadzoe radius definition - if the target is within this radius te robot wil not move
    DEADZONE_RADIUS_IN_PIXELS = 50

    # min motor speed
    MIN_X_MOTOR_SPEED = 100
    MAX_X_MOTOR_SPEED = 255
    K_X = 1.0
    MIN_Y_MOTOR_SPEED = 100
    MAX_Y_MOTOR_SPEED = 255
    K_Y = 1.0

    logging.info('PC Control App')

    # input arguments parser
    logging.info('Parsing input arguments')
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--camera_index", default=-1, type=int,
                    help="camera index")
    parser.add_argument("-t", "--time", default=-1, type=int,
                    help="time of operation in seconds")
    args = parser.parse_args()

    logging.info(f'Opening serial port: {ARDUINO_SERIAL_PORT}...')
    # create a port (it will be automatically opened upon creation)
    try:
        arduino_serial_port = serial.Serial(ARDUINO_SERIAL_PORT)
    except:
        logging.error(f'Serial port {ARDUINO_SERIAL_PORT} could not be opened. Exiting.')
        return

    if not arduino_serial_port.is_open:
        logging.error('Serial port not open.')
    logging.info('Serial port open.')

    cameras = None
    if args.camera_index == -1:
        cameras = get_cameras(max_idx=3)

        if cameras is None:
            logging.error('No cameras found')
            return

        logging.info(f'Found {len(cameras)} camera(s)')
        for key, value in cameras.items():
            logging.info(f'Camera idx: {key}, resolution: {value[0]} x {value[1]}')

        camera_idx = int(input('Select camera index: '))
        logging.info(f'You have selected: {camera_idx}')
    else:
        camera_idx = args.camera_index

    if args.time == -1:
        desired_time = int(input('Enter desired operating time in seconds: '))
    else:
        desired_time = args.time

    # load ArUco marker dictionary
    aruco_dictionary = aruco.Dictionary_get(aruco.DICT_4X4_250)

    # initialize the detector parameters using default values
    parameters =  aruco.DetectorParameters_create()

    # load friendly image
    friendly_img, friendly_w, friendly_h, friendly_corners = load_friendly()
    logging.info(f'Friendly W x H: {friendly_w} x {friendly_h} ')
    foe_img, foe_w, foe_h, foe_corners = load_foe()
    logging.info(f'Foe W x H: {foe_w} x {foe_h} ')

    # get desired damera's image frame width and height
    if cameras is not None:
        width, height = cameras[camera_idx]
    else:
        width, height = get_camera_width_height(camera_idx)

    # calculate camera's image frame center in pixels
    frame_center = (int(width/2), int(height/2))

    # turn on the gun
    send_gun_on(arduino_serial_port)

    # open video stream
    logging.info(f'Opening video stream for camera {camera_idx}...')
    video_capture = cv2.VideoCapture(camera_idx, cv2.CAP_DSHOW)

    logging.info(f'Processing video stream for {desired_time} seconds...')
    start_time = time.time()
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        if elapsed_time > desired_time:
            break

        # get next video frame
        video_frame = video_capture.read()[1]

        # create placeholder for warped image
        warped_image = np.zeros_like(video_frame)

        # detect the markers in the image
        marker_corners, marker_ids, rejected_candidates = aruco.detectMarkers(video_frame, aruco_dictionary, parameters=parameters)

        # apply time left
        display_frame = video_frame.copy()
        display_frame = cv2.putText(display_frame,
            f'Time left: {(desired_time - elapsed_time):.2f}',
            org=(10, 20),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.5,
            color=(0, 255, 0))

        foe_markers = {}

        # apply ArUco ID and corners
        if marker_ids is not None:
            display_frame = cv2.putText(display_frame,
                f'Found {len(marker_ids)} ArUco markers',
                org=(10, 40),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.5,
                color=(0, 255, 0))

            for i, marker_id in enumerate(marker_ids):
                # reshape the corners array to fit findHomography()
                marker_corners_for_current_id = marker_corners[i].reshape(-1, 2)

                # calculate homography between ArUco marker and friendly/foe image
                img_to_warp = None
                if marker_id == FOE_ID:
                    img_to_warp = foe_img
                    homography_matrix, status = cv2.findHomography(foe_corners, marker_corners_for_current_id)
                elif marker_id == FRIENDLY_ID:
                    img_to_warp = friendly_img
                    homography_matrix, status = cv2.findHomography(friendly_corners, marker_corners_for_current_id)

                # transform the source image to fit the ArUco marker
                if img_to_warp is not None:
                    warped_image = cv2.warpPerspective(img_to_warp, homography_matrix, (display_frame.shape[1], display_frame.shape[0]))

                    # replace original pixels of the video frame with pixels from warped image if they are != 0
                    display_frame = np.where(warped_image > 0, warped_image, display_frame)

                # display ArUco marker ID in the top-left corner of the marker
                display_frame = cv2.putText(display_frame,
                    f'ID: {marker_id[0]}',
                    org=(int(marker_corners[i][0, 0, 0] + 10), int(marker_corners[i][0, 0, 1] + 10)),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.5,
                    color=(0, 0, 255))

                # calculate position of the center of ArUco marker
                marker_center_x = int(np.mean(marker_corners[i].reshape(-1, 2), axis=0)[0])
                marker_center_y = int(np.mean(marker_corners[i].reshape(-1, 2), axis=0)[1])

                # draw center of ArUco marker as cross
                display_frame = cv2.drawMarker(display_frame,
                    position=(marker_center_x, marker_center_y),
                    color=(0, 0, 255),
                    markerSize=50)

                # draw all 4 corners of the ArUco marker
                for j, marker_corner in enumerate(marker_corners_for_current_id):
                    display_frame = cv2.drawMarker(display_frame,
                        position=(int(marker_corner[0]),
                        int(marker_corner[1])),
                        color=(0, 0, 255),
                        markerSize=10,
                        markerType=int(j % 4))

                if marker_id == FOE_ID:
                    foe_markers[marker_id[0]] = (marker_center_x, marker_center_y)

        else:
            display_frame = cv2.putText(display_frame,
                'No ArUco markers found',
                org=(10, 40),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.5,
                color=(0, 255, 0))

        # draw deadzone radius
        display_frame = cv2.circle(display_frame,
            center=frame_center,
            radius=DEADZONE_RADIUS_IN_PIXELS,
            color=(0, 255, 0),
            thickness=2)

        if len(foe_markers) > 1:
            # TODO: Support multiple foe targets ???
            logging.warning(f'More than one foe detected. Targeting procedure aborted.')

        if len(foe_markers) == 1:
            # calculate distance between image center and foe markers center
            marker_center_x, marker_center_y = foe_markers[0]

            error_x = marker_center_x - frame_center[0]
            error_y = marker_center_y - frame_center[1]

            # draw error vector
            display_frame = cv2.line(display_frame, pt1=(marker_center_x, marker_center_y), pt2=frame_center, color=(0, 255, 0))

            # calculate X & Y motor speed
            motor_speed_x = calculate_motor_speed(error_x,
                DEADZONE_RADIUS_IN_PIXELS,
                MIN_X_MOTOR_SPEED,
                MAX_X_MOTOR_SPEED,
                K_X)

            motor_speed_y = calculate_motor_speed(error_y,
                DEADZONE_RADIUS_IN_PIXELS,
                MIN_Y_MOTOR_SPEED,
                MAX_Y_MOTOR_SPEED,
                K_Y)

            logging.debug(f'X Error: {error_x}, X Speed: {motor_speed_x}')
            logging.debug(f'Y Error: {error_y}, Y Speed: {motor_speed_y}')

            # set motor speed using Arduino serial port
            send_motor_x_y_speed(arduino_serial_port, motor_speed_x, motor_speed_y)

            # display error and motor speed
            display_frame = cv2.putText(display_frame,
                f'Error X: {error_x}, Speed X: {motor_speed_x}',
                org=(10, 60),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.5,
                color=(0, 255, 0))
            display_frame = cv2.putText(display_frame,
                f'Error Y: {error_y}, Speed Y: {motor_speed_y}',
                org=(10, 80),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.5,
                color=(0, 255, 0))

        # display modified augmented frame
        cv2.imshow(f'Camera Live Feed', display_frame)
        cv2.waitKey(1)

    cv2.destroyAllWindows()
    logging.info('DONE')
    exit(0)


if __name__ == "__main__":
    main()
