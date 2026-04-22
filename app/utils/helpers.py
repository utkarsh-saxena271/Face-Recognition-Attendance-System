import base64
import numpy as np
import cv2

def base64_to_cv2(base64_str):
    # Strip any possible javascript data URI head
    if ',' in base64_str:
        base64_str = base64_str.split(',')[1]
        
    img_data = base64.b64decode(base64_str)
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img
