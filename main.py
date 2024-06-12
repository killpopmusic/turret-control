import time
import RPi.GPIO as GPIO
from picamera2 import Picamera2, Preview
import cv2
import numpy as np

'''
Main controlling script integrating:

-vision detecting algorith (circle_detector.py)
-continuous movement in yaw axis while searching for a target
-centering the cannon at the detected target and gooting using Airsoft Gearbox

'''
# RPi 4b GPIO setup:

servo_pin_yaw = 19  # Pin for yaw servo
servo_pin_pitch = 18 
shooting_pin = 17  # Pin connected to the shooting gearbox

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin_yaw, GPIO.OUT)
GPIO.setup(shooting_pin, GPIO.OUT)  # Set pin as an output
GPIO.setup(servo_pin_pitch, GPIO.OUT)

# Setup PWM
pwm_yaw = GPIO.PWM(servo_pin_yaw, 50)  # 50Hz <-> period = 20ms according to datasheet
pwm_yaw.start(0)

pwm_pitch = GPIO.PWM(servo_pin_pitch, 50)  # 50Hz <-> period = 20ms according to datasheet
pwm_pitch.start(0)


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

#Shooting function performing 1 shot with the connected gearbox
def shoot():
    # Set GPIO pin high (1)
    GPIO.output(shooting_pin, GPIO.HIGH)
    time.sleep(0.2)  # Time adjusted for a single shot 
    # Set GPIO pin low (0)
    GPIO.output(shooting_pin, GPIO.LOW)


#Function to minimize the error between tharget's center and the cannon
def adjust_position(current_yaw, current_pitch, target_x, target_y, screen_center_x, screen_center_y):
    error_x = target_x - screen_center_x
    print("Error X:", error_x)
    error_y = target_y - screen_center_y
    print("Error Y:", error_y)

    # Calculate new yaw and pitch based on the error

    new_yaw = current_yaw + error_x / 25.0  # Adjust the divisor for sensitivity
    new_pitch = current_pitch + error_y / 20.0  # Adjust the divisor for sensitivity

    # Constrain pitch within 10-35 degrees
    new_pitch = max(10, min(30, new_pitch))

    print("New yaw:", new_yaw)
    print("New pitch", new_pitch)


    return new_yaw, new_pitch

#Simple set angle function 
def set_angle(pwm, angle):
    duty = (angle / 18) + 2
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)

#Function containing the main loop 
def move_yaw_and_detect():
    # Established parameters for continuous movement, not smooth due to mechanical issues 
    start_yaw = 10
    start_pitch =25
    end_yaw = 40
    increment = 2 #adjust increment and delay to smoothen the servo movement 
    delay = 0.5

    picam2 = Picamera2()
    config = picam2.create_preview_configuration({'format': 'BGR888', 'size': (640, 480)}) #setting the resolution added 
    picam2.configure(config)
    picam2.start()

    screen_center_x = 640 / 2  # Assuming 640x480 resolution
    screen_center_y = 480 / 2

    k = 0
    current_yaw = start_yaw
    current_pitch = 25  # Start with the cannon looking straight ahead
    set_angle(pwm_pitch, start_pitch)# for now just set pitch on start up, can be looped later 


    while True:
        # Move the servo
        while current_yaw <= end_yaw:
            set_angle_smooth(pwm_yaw, current_yaw, current_yaw + increment, increment, delay)
            current_yaw += increment

            # Capture and process image
            yuv = picam2.capture_array()
            img = cv2.cvtColor(yuv, cv2.COLOR_BGR2HSV)
            result = yuv.copy()

            lower = np.array([95, 160, 100])  # Adjust HSV values as needed
            upper = np.array([145, 255, 255])
            mask = cv2.inRange(img, lower, upper)

            result = cv2.bitwise_and(result, result, mask=mask)
            result = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)
            _, thr = cv2.threshold(result, 5, 255, cv2.THRESH_BINARY)
            thr = cv2.cvtColor(thr, cv2.COLOR_BGR2GRAY)

            circles = None
            if thr.dtype == 'uint8':
                circles = cv2.HoughCircles(thr, cv2.HOUGH_GRADIENT, 1, thr.shape[0] / 8,
                                           param1=100, param2=21, minRadius=30, maxRadius=80)

            if circles is not None:
                time.sleep(1.0)
                print("Target detected!")
                circles = np.uint16(np.around(circles))
                a = np.array(circles[0])
                if a.shape[0] > 1:
                    a = a[a[:, 2].argsort()[::-1]]

                # Center - x, y coordinates and radius
                center = (a[0][0], a[0][1])
                radius = a[0][2]
                print(center)

                # Adjust position to center the cannon on the target
                # Optionally adjust  position taking into account the camera offset
                camera_offset = 0  #distance in y between the cannon and camera 
                adjusted_center_y = center[1] + camera_offset
                print("Adjusted y:", adjusted_center_y)

                current_yaw, current_pitch = adjust_position(current_yaw, current_pitch, center[0], adjusted_center_y, screen_center_x, screen_center_y)

                # Set new angles
                set_angle(pwm_yaw, current_yaw)
                set_angle(pwm_pitch, current_pitch)

                # Shoot
                shoot()
                set_angle(pwm_pitch, start_pitch)
                break

            k += 1

        current_yaw = start_yaw
        current_pitch = start_pitch

    # Cleanup
    pwm_yaw.stop()
    pwm_pitch.stop()
    GPIO.cleanup()

# Start the combined yaw movement and vision processing
move_yaw_and_detect()
