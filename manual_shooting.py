'''
Script for manual shooting command from user, not dependent on the vision 
'''
import time
import threading
import RPi.GPIO as GPIO

# Movement config
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

# Global flag for stopping continuous movement
stop_continuous_movement = threading.Event()

#Quick and simple  set angle function 
def set_angle(pwm, axis, angle):

    duty = (angle / 18) + 2  # Convert angle to duty cycle
    #GPIO.output(axis, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    #GPIO.output(axis, False)
    pwm.ChangeDutyCycle(0)

# Function to set angle for a yaw  servo slowly
def set_angle_smooth(pwm, start_angle, end_angle, increment, delay):

    if start_angle < end_angle:
        angle_range = range(start_angle, end_angle + 1, increment)
    else:
        angle_range = range(start_angle, end_angle - 1, -increment)
    
    for angle in angle_range:
        if stop_continuous_movement.is_set():
            break
        duty = (angle / 18) + 2  # Convert angle to duty cycle
        pwm.ChangeDutyCycle(duty)
        time.sleep(delay)
    pwm.ChangeDutyCycle(0)

def move_yaw():
    # Established parameters for continuous movement
    start_yaw = 10
    end_yaw = 180
    increment = 1
    delay = 0.03

    try:
        while not stop_continuous_movement.is_set():
            current_yaw = start_yaw
            while current_yaw <= end_yaw and not stop_continuous_movement.is_set():
                set_angle_smooth(pwm_yaw, current_yaw, current_yaw + increment, increment, delay)
                current_yaw += increment

            current_yaw = end_yaw
            while current_yaw >= start_yaw and not stop_continuous_movement.is_set():
                set_angle_smooth(pwm_yaw, current_yaw, current_yaw - increment, increment, delay)
                current_yaw -= increment

    except KeyboardInterrupt:
        pass

def listen_for_stop():
    while not stop_continuous_movement.is_set():
        user_input = input("Type 's' to shoot ").strip().lower()
        if user_input == "s":
            stop_continuous_movement.set()
            set_angle(pwm_pitch,servo_pin_pitch,15)
            print("Shooting command received")


# Start the continuous yaw movement in a separate thread
movement_thread = threading.Thread(target=move_yaw)
movement_thread.start()

# Listen for user command in the main thread
listen_for_stop()

# Wait for the movement thread to finish
movement_thread.join()

# Cleanup
pwm_yaw.stop()
GPIO.cleanup()
