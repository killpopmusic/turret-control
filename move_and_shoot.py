import time
import RPi.GPIO as GPIO
from picamera2 import Picamera2, Preview
import cv2
import numpy as np

'''
Script for integrating vision lagorithm with movement logic - turret to move continously in yaw
axis and stop when target is detected

For now - no pitch movements 

'''
# Movement config
servo_pin_yaw = 19  # Pin for yaw servo

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin_yaw, GPIO.OUT)

# Setup PWM
pwm_yaw = GPIO.PWM(servo_pin_yaw, 50)  # 50Hz <-> period = 20ms according to datasheet
pwm_yaw.start(0)

# Function to set angle for a servo smoothly
def set_angle_smooth(pwm, start_angle, end_angle, increment, delay):
    if start_angle < end_angle:
        angle_range = range(start_angle, end_angle + 1, increment)
    else:
        angle_range = range(start_angle, end_angle - 1, -increment)
    
    for angle in angle_range:
        duty = (angle / 18) + 2  # Convert angle to duty cycle
        pwm.ChangeDutyCycle(duty)
        time.sleep(delay)
    pwm.ChangeDutyCycle(0)

def move_yaw_and_detect():
    #established parameteres for continous movement, not smooth due to mechanical issues 
    start_yaw = 10
    end_yaw = 180
    increment = 1
    delay = 0.03

    picam2 = Picamera2()
    config = picam2.create_preview_configuration({'format': 'BGR888'})
    picam2.configure(config)
    picam2.start()

    k = 0
    start_time = time.monotonic()
    delay_time = 20
    target_detected = False

    #Vision loop 

    while time.monotonic() - start_time < delay_time and not target_detected:
        # Move the servo
        current_yaw = start_yaw
        while current_yaw <= end_yaw and not target_detected:
            set_angle_smooth(pwm_yaw, current_yaw, current_yaw + increment, increment, delay)
            current_yaw += increment

            # Capture and process image
            yuv = picam2.capture_array()
            img = cv2.cvtColor(yuv, cv2.COLOR_BGR2HSV)
            result = yuv.copy()

            lower = np.array([95, 160, 100])# red ~120 hsv
            upper = np.array([145, 255, 255])
            mask = cv2.inRange(img, lower, upper)

            result = cv2.bitwise_and(result, result, mask=mask)
            result = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)
            _, thr = cv2.threshold(result, 5, 255, cv2.THRESH_BINARY)
            thr = cv2.cvtColor(thr, cv2.COLOR_BGR2GRAY)

            circles = None
            if thr.dtype == 'uint8':
                circles = cv2.HoughCircles(thr, cv2.HOUGH_GRADIENT, 1, thr.shape[0] / 8,
                                           param1=100, param2=21, minRadius=35, maxRadius=80)

            if circles is not None:
                print("Target detected!")
                target_detected = True
                circles = np.uint16(np.around(circles))
                a = np.array(circles[0])
                if a.shape[0] > 1:
                    a = a[a[:, 2].argsort()[::-1]]

                # center - x, y coordinates and radius
                center = (a[0][0], a[0][1])
                radius = a[0][2]
                #cv2.circle(yuv, center, radius, (255, 0, 255), 3)
                #cv2.imwrite("yep"+str(k)+".jpg", yuv)
        
        
        
                #cv2.imwrite("thr"+str(k)+".jpg", thr)

                break

            k += 1

    # Cleanup
    pwm_yaw.stop()
    GPIO.cleanup()

# Start the combined yaw movement and vision processing
move_yaw_and_detect()
