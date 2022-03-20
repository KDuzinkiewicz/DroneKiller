import cv2
import logging
import time
import cv2.aruco as aruco

from cv2 import VideoCapture


# set root logger log level
logging.getLogger().setLevel(logging.INFO)


def get_cameras(max_idx=10):
    '''
    Gets a dictionary of camera indices and friendly names

    Parameters:
        max_idx (int): up to what idex to enumerate

    Returns:
        cameras (dict): key = camera index, value = camera friendly name
    '''

    logging.info('Enumerating cameras...')

    cameras = {}

    for i in range(max_idx + 1):
        logging.info(f'Analyzing camera idex: {i}/{max_idx}...')
        video_capture = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if not video_capture.read()[0]:
            logging.info(f'Invalid camera index')
            continue
        else:
            logging.info(f'Camera available')
            width = video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
            cameras[i] = (width, height)
        video_capture.release()

    return cameras

def main():

    logging.info('Dummy Camera Example')
    cameras = get_cameras(max_idx=3)

    # load ArUco marker dictionary
    aruco_dictionary = aruco.Dictionary_get(aruco.DICT_4X4_250)

    # initialize the detector parameters using default values
    parameters =  aruco.DetectorParameters_create()

    if cameras is None:
        logging.error('No cameras found')
        return

    logging.info(f'Found {len(cameras)} camera(s)')
    for key, value in cameras.items():
        logging.info(f'Camera idx: {key}, resolution: {value[0]} x {value[1]}')

    camera_idx = int(input('Select camera index: '))
    logging.info(f'You have selected: {camera_idx}')
    desired_time = int(input('Enter desired operating time in seconds: '))

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

        # apply ArUco ID and corners
        if marker_ids is not None:
            display_frame = cv2.putText(display_frame,
                f'Found {len(marker_ids)} ArUco markers',
                org=(10, 40),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.5,
                color=(0, 255, 0))

            for i, marker_id in enumerate(marker_ids):
                # display ArUco marker ID in the top-left corner of the marker
                display_frame = cv2.putText(display_frame,
                    f'ID: {marker_id[0]}',
                    org=(int(marker_corners[i][0, 0, 0]), int(marker_corners[i][0, 0, 1])),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.5,
                    color=(0, 255, 0))
        else:
            display_frame = cv2.putText(display_frame,
                'No ArUco markers found',
                org=(10, 40),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.5,
                color=(0, 255, 0))

        # display modified augmented frame
        cv2.imshow(f'Camera Live Feed', display_frame)
        cv2.waitKey(1)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
