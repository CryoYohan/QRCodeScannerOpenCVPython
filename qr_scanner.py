from pyzbar.pyzbar import decode
import cv2
import numpy as np

class QRScanner:
    def __init__(self) -> None:
        self.img_granted = cv2.imread("images/access-granted.jpg", cv2.IMREAD_COLOR) 
        self.img_denied = cv2.imread("images/access-denied.jpg", cv2.IMREAD_COLOR)   
    
    @staticmethod
    def read_qr_code(image):        
        return decode(image)
    
    @staticmethod
    def add_box_to_qr_code(image, barcode):        
        pts = np.array([barcode.polygon], np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(image, [pts], True, (128, 0, 128), 5)
        
    @staticmethod
    def encode(image):        
        ret, buffer = cv2.imencode(".jpg", image)
        return buffer.tobytes()
    
    def get_access_granted_img(self):           
        return self.img_granted
    
    def get_access_denied_img(self):             
        return self.img_denied
    
        