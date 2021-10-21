import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

class Pen:
    def __init__(self, servopin_number): #21
        GPIO.setup(servopin_number, GPIO.OUT)
        self.pin = GPIO.PWM(servopin_number, 50) # GPIO 17 for PWM with 50Hz (20ms)
        self.pin.start(2.5) # Initialization
        print("pen starting...")
    def angle(self, angle):
        duty_cycle = self.angle_to_dc(angle)
        self.spin_motor(duty_cycle, 0.45) ############# wait 0.45 sec to make sure complete turn can be done, but later reduce to what is actually needed for this specific turn
    def angle_to_dc(self, a):
        # 0 deg = 2.5 // 180 deg = 12
        return 2.5 + 9*a/180
    def down(self, p): # True is down
        a=80 if p else 20
        self.angle(a) 
    def spin_motor(self, duty_cycle, wait):
        self.pin.ChangeDutyCycle(duty_cycle)
        time.sleep(wait)         # enough time to make a full turn
        self.pin.ChangeDutyCycle(0)  # to stop the jittering of the arm
        time.sleep(0.1)           # wait before next step
    def finishup(self):   
        self.pin.stop()
        GPIO.cleanup()

