## Code below defines a shoot function performing a single shot from a gearbox 

import RPi.GPIO as GPIO
import time

# Adjust the pin with gearbox steering
shooting_pin = 17  # Pin connected to the shooting gearbox

GPIO.setwarnings(False)  # Disable GPIO warnings
GPIO.setmode(GPIO.BCM)  # Use BCM numbering
GPIO.setup(shooting_pin, GPIO.OUT)  # Set pin as an output

def shoot():
    # Set GPIO pin high (1)
    GPIO.output(shooting_pin, GPIO.HIGH)
    time.sleep(0.15)  # Time adjusted for a single shot 
    # Set GPIO pin low (0)
    GPIO.output(shooting_pin, GPIO.LOW)

try:
    shoot()
finally:
    # Cleanup GPIO settings
    GPIO.cleanup()
