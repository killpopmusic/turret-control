import time
import RPi.GPIO as GPIO
from picamera2 import Picamera2, Preview
import cv2
import numpy as np

# Movement config
servo_pin_yaw = 19  # Pin for yaw servo
servo_pin_pitch = 18  # Pin for pitch servo
shooting_pin = 17  # Pin connected to the shooting gearbox

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin_yaw, GPIO.OUT)
GPIO.setup(servo_pin_pitch, GPIO.OUT)
GPIO.setup(shooting_pin, GPIO.OUT)

# Setup PWM
pwm_yaw = GPIO.PWM(servo_pin_yaw, 50)  # 50Hz <-> period = 20ms according to datasheet
pwm_pitch = GPIO.PWM(servo_pin_pitch, 50)
pwm_yaw.start(0)
pwm_pitch.start(0)

# Safe starting position [deg]
start_yaw = 90
start_pitch = 100

# Set initial positions
pwm_yaw.ChangeDutyCycle((start_yaw / 18) + 2)
time.sleep(0.5)
pwm_pitch.ChangeDutyCycle((start_pitch / 18) + 2)
time.sleep(0.5)

# Function to set angle for a servo (to be calibrated exactly)
def set_angle(pwm, angle):
    duty = (angle / 18) + 2  # Convert angle to duty cycle
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.02)  # Short delay to stabilize the servo

# Function to shoot
def shoot():
    # Set GPIO pin high (1)
    GPIO.output(shooting_pin, GPIO.HIGH)
    time.sleep(0.15)  # Time adjusted for a single shot 
    # Set GPIO pin low (0)
    GPIO.output(shooting_pin, GPIO.LOW)

# Camera setup
picam2 = Picamera2()
config = picam2.create_preview_configuration({'format': 'BGR888', 'size': (1280, 720)})
picam2.configure(config)
picam2.start()

k = 0
start_time = time.monotonic()

# Time of running the program (20 seconds)
delay_time = 10

# Screen center coordinates
screen_center_x = 1280 / 2  # assuming 1280x720 resolution
screen_center_y = 720 / 2

# Tolerance for centering
tolerance = 10

# Initialize the last shot time
last_shot_time = 0

# Movement range for the servos
yaw_min = 0
yaw_max = 180
pitch_min = 90
pitch_max = 120

current_yaw = start_yaw
current_pitch = start_pitch

while time.monotonic() - start_time < delay_time:
    yuv = picam2.capture_array()
    img = cv2.cvtColor(yuv, cv2.COLOR_BGR2HSV)
    result = yuv.copy()
    
    lower = np.array([95, 160, 100])
    upper = np.array([145, 255, 255])
    mask = cv2.inRange(img, lower, upper)
    
    result = cv2.bitwise_and(result, result, mask=mask)
    result = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)
    _, thr = cv2.threshold(result, 5, 255, cv2.THRESH_BINARY)
    thr = cv2.cvtColor(thr, cv2.COLOR_BGR2GRAY)
    
    circles = None
    if thr.dtype == 'uint8':
        circles = cv2.HoughCircles(thr, cv2.HOUGH_GRADIENT, 1, thr.shape[0] / 8,
                                   param1=100, param2=21, minRadius=25, maxRadius=80)
    
    if circles is not None:
        print("Target detected!")
        circles = np.uint16(np.around(circles))
        a = np.array(circles[0])
        if a.shape[0] > 1:
            a = a[a[:, 2].argsort()[::-1]]
        
        # center - x, y coordinates and radius
        center = (a[0][0], a[0][1])
        radius = a[0][2]

        # Calculate error
        error_x = center[0] - screen_center_x
        error_y = center[1] - screen_center_y

        # Adjust yaw
        if abs(error_x) > tolerance:
            current_yaw += -error_x / 50.0  # Adjust this divisor for sensitivity
            current_yaw = max(yaw_min, min(yaw_max, current_yaw))
            set_angle(pwm_yaw, int(current_yaw))

        # Adjust pitch
        if abs(error_y) > tolerance:
            current_pitch += error_y / 50.0  # Adjust this divisor for sensitivity
            current_pitch = max(pitch_min, min(pitch_max, current_pitch))
            set_angle(pwm_pitch, int(current_pitch))

        # If the target is centered, shoot
        if abs(error_x) <= tolerance and abs(error_y) <= tolerance:
            if time.monotonic() - last_shot_time > 5:
                print("Shooting...")
                shoot()
                last_shot_time = time.monotonic()
    
    else:
        # Move yaw continuously if no circle is detected
        current_yaw += 1  # Adjust this for your scanning speed
        if current_yaw > yaw_max:
            current_yaw = yaw_min
        set_angle(pwm_yaw, int(current_yaw))
    
    k += 1

# Cleanup
pwm_yaw.stop()
pwm_pitch.stop()
GPIO.cleanup()
