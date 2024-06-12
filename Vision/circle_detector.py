import time
from picamera2 import Picamera2, Preview, MappedArray
import cv2
import numpy as np


picam2 = Picamera2()
# preview wont't work on this configuration
#picam2.start_preview(Preview.QTGL)
config = picam2.create_preview_configuration({'format': 'BGR888'})
picam2.configure(config)

k=0

picam2.start()

start_time = time.monotonic()

# time of running the program (20 seconds)
delay_time = 20

while time.monotonic() - start_time < delay_time:
    yuv = picam2.capture_array()
    img = cv2.cvtColor(yuv, cv2.COLOR_BGR2HSV)
    result = yuv.copy()
    
    lower = np.array([95, 160, 100])
    upper = np.array([145, 255, 255])
    mask = cv2.inRange(img, lower, upper)
    
    result = cv2.bitwise_and(result, result, mask = mask)
    result = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)
    _, thr = cv2.threshold(result, 5, 255, cv2.THRESH_BINARY)
    thr = cv2.cvtColor(thr, cv2.COLOR_BGR2GRAY)
    
    circles = None
    if thr.dtype == 'uint8':
        circles = cv2.HoughCircles(thr, cv2.HOUGH_GRADIENT, 1, thr.shape[0]/8,
                                   param1=100, param2=21, minRadius=25, maxRadius=80)
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        a = np.array(circles[0])
        if a.shape[0] > 1:
            a = a[a[:,2].argsort()[::-1]]
        
        # center - x, y coordinates and radius
        center = (a[0][0], a[0][1])
        radius = a[0][2]
        
        # to check results uncomment both below - it will save frames to files
        #cv2.circle(yuv, center, radius, (255, 0, 255), 3)
        #cv2.imwrite("yep"+str(k)+".jpg", yuv)
        
        
        
        #cv2.imwrite("thr"+str(k)+".jpg", thr)
    k = k+1
     
    
    
    
    
    

