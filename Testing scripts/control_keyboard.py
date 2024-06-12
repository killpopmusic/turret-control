import RPi.GPIO as GPIO
import time
import curses

#Establish the pins below: 

servo1_pin = 18  # Yaw angle servo
servo2_pin = 19  # Pitch angle servo

GPIO.setwarnings(False)  # Disable GPIO warnings
GPIO.setmode(GPIO.BCM)  # Use BCM numbering
GPIO.setup(servo1_pin, GPIO.OUT)
GPIO.setup(servo2_pin, GPIO.OUT)

# Setup PWM
pwm1 = GPIO.PWM(servo1_pin, 50)  # 50Hz frequency for yaw servo
pwm2 = GPIO.PWM(servo2_pin, 50)  # 50Hz frequency for pitch servo

pwm1.start(0)
pwm2.start(0)

#Safe initial values 

yaw_angle = 100  # Initial yaw angle
pitch_angle = 100  # Initial pitch angle within constraints

def set_angle(pwm, angle):
    duty = (angle / 18) + 2  # Convert angle to duty cycle
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.01)  # Small delay for smoother movement

def main(stdscr):
    global yaw_angle, pitch_angle
    
    # Clear screen
    stdscr.clear()
    
    while True:

        key = stdscr.getch()
        
        if key == ord('w') and pitch_angle < 155:
            pitch_angle += 3
            set_angle(pwm2, pitch_angle)
        elif key == ord('s') and pitch_angle > 90:
            pitch_angle -= 3
            set_angle(pwm2, pitch_angle)
        elif key == ord('a') and yaw_angle > 0:
            yaw_angle -= 1
            set_angle(pwm1, yaw_angle)
        elif key == ord('d') and yaw_angle < 180:
            yaw_angle += 1
            set_angle(pwm1, yaw_angle)

        stdscr.refresh()
        time.sleep(0.01)  # Reduce CPU usage

try:
    curses.wrapper(main)
except KeyboardInterrupt:
    pass

# Cleanup
pwm1.stop()
pwm2.stop()
GPIO.cleanup()
