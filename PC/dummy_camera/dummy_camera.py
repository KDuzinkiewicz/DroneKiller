import cv2
import logging
import time

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
        video_frame = video_capture.read()[1]
        cv2.imshow('Camera Feed', video_frame)
        cv2.waitKey(1)
        current_time = time.time()
        elapsed_time = current_time - start_time
        if elapsed_time > desired_time:
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
