import cv2
import cv2.aruco as aruco
import numpy as np

MARKER_SIZE_IN_MM = 200

marker_id = int(input(f'Enter marker ID: '))

# load the predefined dictionary
dictionary = aruco.Dictionary_get(aruco.DICT_4X4_250)

# generate the marker image
markerImage = np.zeros((MARKER_SIZE_IN_MM, MARKER_SIZE_IN_MM), dtype=np.uint8)
markerImage = aruco.drawMarker(dictionary, marker_id, MARKER_SIZE_IN_MM, markerImage, 1)
cv2.imwrite(f'marker_id{marker_id}.png', markerImage)
