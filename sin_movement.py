### Test sinusoidal  movement on both axes - 

# TO DO: Smoothen the movement 

import RPi.GPIO as GPIO
import time
import math

# GPIO setup
servo1_pin = 19  # Use the pin you connected to the first servo signal wire (PWM pin)
servo2_pin = 18  

GPIO.setmode(GPIO.BCM)  # Use BCM numbering
GPIO.setup(servo1_pin, GPIO.OUT)
GPIO.setup(servo2_pin, GPIO.OUT)

# Setup PWM
pwm1 = GPIO.PWM(servo1_pin, 50)  # 50Hz frequency for first servo
pwm2 = GPIO.PWM(servo2_pin, 50)  # 50Hz frequency for second servo

pwm1.start(0)
pwm2.start(0)

def set_angle(pwm, angle):
    duty = (angle / 18) + 2  # Convert angle to duty cycle
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.01)  # Small delay for smoother movement

try:
    while True:
        for i in range(180):  # One full sine wave cycle
            angle1 = 92 + (math.sin(math.radians(i)) * 63)  # Adjust scaling for smoothness
            angle2 = (math.sin(math.radians(i)) * 90)  # 90 degree phase shift for second servo

            set_angle(pwm1, angle1)
            set_angle(pwm2, angle2)
            time.sleep(0.005)  # Reduce sleep time for smoother movement
except KeyboardInterrupt:
    pass

# Cleanup
pwm1.stop()
pwm2.stop()
