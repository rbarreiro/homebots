import cv2
import cv2.aruco as aruco
from utils import show_img
import numpy as np

def create_aruco(marker_id):
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
    marker_size = 400
    marker_image = np.zeros((marker_size, marker_size, 1), dtype=np.uint8)
    return aruco.generateImageMarker(aruco_dict, marker_id, marker_size, marker_image, 1)

def detect_aruco(frame):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Define the ArUco dictionary
    # Note: Use the same dictionary type that was used to create the marker
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    
    # Create parameters and detector
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    
    # Detect markers
    corners, ids, rejected = detector.detectMarkers(gray)
        
    return ids, corners

def generate_aruco():
    # corners ids
    # 0 1
    # 3 2
    i = 0
    aruco_code=create_aruco(i)
    show_img(aruco_code)
    cv2.imwrite("aruco" + str(i) + ".jpg", aruco_code)

class Camera:
    def __init__(self, url, rotate180=False):
        self._url = url
        self._rotate180 = rotate180
#        self._capture = cv2.VideoCapture(url)
#        if not self._capture.isOpened():
#            raise Exception("Não foi possível abrir a câmara.")
        
    def get_frame(self):
        capture = cv2.VideoCapture(self._url)
        ret, frame = capture.read()
        capture.release()
        if not ret:
            raise Exception("Não foi possível ler o frame da câmara.")
        if self._rotate180:
            return cv2.rotate(frame, cv2.ROTATE_180)
        else:
            return frame
        
    
    def show_frame(self):
        show_img(self.get_frame())

    def detect_arucos(self):
        return detect_aruco(self.get_frame())
    
    def show_arucos(self):
        frame = self.get_frame()
        ids, corners = detect_aruco(frame)
        detections =cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        show_img(detections)