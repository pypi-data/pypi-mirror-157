import sys
import os.path
if sys.platform == 'win32' or not __package__:
    sys.path.append(os.path.dirname(__file__))
    from simulator import GPIO
else:
	from RPi.GPIO import GPIO

if __package__:
    from . import Adafruit_PWM_Servo_Driver as servo_drv # Adafruit Industries 是纽约的一家开源硬件公司
else:
    import Adafruit_PWM_Servo_Driver as servo_drv
import time

RUNNING = True
DELTA = 5 # degrees to to correct servo direction. 
PT_STEP = 5
IIC_SERVO = 0x40

# Initialise the servo PWM using the default address
servo_pwm = servo_drv.PWM(IIC_SERVO, debug = False)
servoMin = 150  # Min pulse length out of 4096
servoMax = 600  # Max pulse length out of 4096

def setServoPulse(channel, pulse):
    pulseLength = 1000000.0                   # 1,000,000 us per second
    pulseLength /= 50.0                       # 60 Hz
    # print ("%d us per period", pulseLength)
    pulseLength /= 4096.0                     # 12 bits of resolution
    # print ("%d us per bit", pulseLength)
    pulse *= 1000.0
    pulse /= (pulseLength*1.0)
    # pwmV=int(pluse)
    # print ("pluse: %f  ", pulse)
    servo_pwm.setPWM(channel, 0, int(pulse))

#Angle to PWM
def turn_direction(servonum,x):
    x = x + DELTA
    y=x/90.0+0.5
    y=max(y,0.5)
    y=min(y,2.5)
    setServoPulse(servonum,y)

def pan_tilt_right():
    global PT_LR
    PT_LR = PT_LR - PT_STEP
    if (PT_LR < 0):
        PT_LR = 0
    turn_direction(1,PT_LR)

def pan_tilt_left():
    global PT_LR
    PT_LR = PT_LR + PT_STEP
    if (PT_LR > 180):
        PT_LR = 180
    turn_direction(1,PT_LR)

def pan_tilt_up():
    global PT_UD
    PT_UD = PT_UD - PT_STEP
    if (PT_UD < 0):
        PT_UD = 0
    turn_direction(2,PT_UD)

def pan_tilt_down():
    global PT_UD
    PT_UD = PT_UD + PT_STEP
    if (PT_UD > 135):
        PT_UD = 135
    turn_direction(2,PT_UD)

def pan_tilt(status): # Pan-Tilt
    '''
    'up3x', 'up2x', 'up1x', \
	'down3x', 'down2x', 'down1x', \
	'left3x', 'left2x', 'left1x', \
	'right3x', 'right2x', 'right1x', \
	'pressed'
    '''    

    if 'up' in status:
        pan_tilt_up()
    if 'down' in status:
        pan_tilt_down()
    if 'left' in status:
        pan_tilt_left()
    if 'right' in status:
        pan_tilt_right()
   
    # time.sleep(0.5)

def test_servo():

    for ch in [0,1,2,3]:
        for ang in [70, 90]: # [30,60,90,120,150,90]:
            turn_direction(ch,ang)
            time.sleep(0.5)
    
def setup():
    servo_pwm.setPWMFreq(50)   # Set frequency

    global PT_LR, PT_UD
    PT_LR = 90
    PT_UD = 90

def destroy():
	GPIO.cleanup()  # 释放资源

if __name__ == "__main__":
	try:  
		setup()      
		test_servo()        
	except KeyboardInterrupt:                             
		destroy()