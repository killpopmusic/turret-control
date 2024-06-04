import cv2
import numpy as np
import RPi.GPIO as GPIO
import time

'''
MAIN CONTROL SCRIPT 

GPIO set according to default configuration that can be found in README

Data to be taken into account: 

- Camera's FOV (75 deg for Picamera3?)
- Pitch movement contraints and servo starting positions 
- Duty cycles for limit angle values may vary in each servo 

'''
# GPIO setup

#movement
servo_pin_yaw = 18  # Pin for yaw servo
servo_pin_pitch = 19  # Pin for pitch servo

#shooting
shooting_pin = 17  # Pin connected to the shooting gearbox

GPIO.setwarnings(False) #ez
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin_yaw, GPIO.OUT)
GPIO.setup(servo_pin_pitch, GPIO.OUT)

# Setup PWM
pwm_yaw = GPIO.PWM(servo_pin_yaw, 50)  # 50Hz <-> period = 20ms according to datasheet
pwm_pitch = GPIO.PWM(servo_pin_pitch, 50)  
pwm_yaw.start(0)
pwm_pitch.start(0)

# safe starting position [deg]
start_yaw = 90
start_pitch = 100

# Function to set angle for a servo (to be calibrated exactly)
def set_angle(pwm, angle):

    duty = (angle / 18) + 2  # Convert angle to duty cycle
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)

# Mapping cords to angles 

def map_coord_to_angle(x, y, width, height, hFoV, vFoV, min_yaw, max_yaw, min_pitch, max_pitch):

    # Calculate the center of the image
    center_x, center_y = width / 2, height / 2
    
    # Calculate the pixel to degree conversion factors
    h_degrees_per_pixel = hFoV / width
    v_degrees_per_pixel = vFoV / height
    
    # Calculate the offset from the center in pixels
    offset_x = x - center_x
    offset_y = center_y - y  # Invert y axis (top to bottom), to be ckecked, usually opencv does this conversion
    
    # Convert pixel offset to angle offset
    angle_offset_yaw = offset_x * h_degrees_per_pixel
    angle_offset_pitch = offset_y * v_degrees_per_pixel
    
    # Map the offsets to the servo angle range
    center_yaw = (min_yaw + max_yaw) / 2
    center_pitch = (min_pitch + max_pitch) / 2
    
    angle_yaw = center_yaw + angle_offset_yaw
    angle_pitch = center_pitch + angle_offset_pitch
    
    return angle_yaw, angle_pitch

# Function to perform a shoot action
def shoot():
    print("Shoot attempt")
   
    #GPIO.output(shooting_pin, GPIO.HIGH)
    #time.sleep(0.15)  # Time adjusted for a single shot 
    
    #GPIO.output(shooting_pin, GPIO.LOW)


# Function to move servos to a specific angle and then back to the start position
def move_and_shoot(x, y, width, height, hFoV, vFoV, min_yaw, max_yaw, min_pitch, max_pitch):

    # Map coordinates to angles
    angle_yaw, angle_pitch = map_coord_to_angle(x, y, width, height, hFoV, vFoV, min_yaw, max_yaw, min_pitch, max_pitch)
    
    # Move servos to target position
    set_angle(pwm_yaw, angle_yaw)
    set_angle(pwm_pitch, angle_pitch)
    
    # Shoot
    shoot()
    
    # Move servos back to start position
    set_angle(pwm_yaw, start_yaw)
    set_angle(pwm_pitch, start_pitch)

# Function to get target coordinates from camera feed
def get_target_coordinates(cap):

    # Vision algoritm returning X and Y olny if target detected
    pass


try:
    cap = cv2.VideoCapture(0)  # Open the default camera
    
    while True:
        # Get target coordinates from the vision algorithm
        coords = get_target_coordinates(cap)
        if coords is not None:
            x, y = coords
            
            # Assume a resolution of 640x480 for the camera
            width, height = 640, 480
            
            # Assume the field of view of the camera in degrees
            hFoV = 76  # Horizontal field of view in degrees
            vFoV = 76  # Vertical field of view in degrees (assuming square aspect ratio)
            
            # Servo angle limits
            min_yaw, max_yaw = 0, 180
            min_pitch, max_pitch = 90, 155
            
            # Move, shoot, and return to start position
            move_and_shoot(x, y, width, height, hFoV, vFoV, min_yaw, max_yaw, min_pitch, max_pitch)
        
except KeyboardInterrupt:
    pass

finally:

    cap.release()  # Release the camera resource
    pwm_yaw.stop()
    pwm_pitch.stop()
    GPIO.cleanup()
