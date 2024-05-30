import RPi.GPIO as GPIO
import time

# GPIO setup
servo_pin = 18  # Use the pin you connected to the servo signal wire (PWM pin)
GPIO.setmode(GPIO.BCM)  # Use BCM numbering
GPIO.setup(servo_pin, GPIO.OUT)

# Setup PWM
pwm = GPIO.PWM(servo_pin, 50)  # 50Hz frequency for servo
pwm.start(0)

def set_angle(angle):
    duty = (angle / 18) + 2  # Convert angle to duty cycle
    GPIO.output(servo_pin, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(servo_pin, False)
    pwm.ChangeDutyCycle(0)

try:
    while True:
        angle = input("Enter angle (0 to 180): ")
        if angle.lower() == 'exit':
            break
        angle = int(angle)
        if 0 <= angle <= 180:
            set_angle(angle)
        else:
            print("Please enter a value between 0 and 180.")
except KeyboardInterrupt:
    pass

# Cleanup
pwm.stop()
GPIO.cleanup()
