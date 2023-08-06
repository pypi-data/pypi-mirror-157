import sys
import os.path
if sys.platform == 'win32':
    sys.path.append(os.path.dirname(__file__))
    from simulator import GPIO
else:
	from RPi.GPIO import GPIO

import time
import sys
import os.path

if __package__:
    from . import servo, led, joystick, passive_buzzer as pbz
    from .liquidcrystal_i2c import LiquidCrystal_I2C
else:
    sys.path.append(os.path.dirname(__file__))
    import servo, led, joystick, passive_buzzer as pbz
    from liquidcrystal_i2c import LiquidCrystal_I2C
'''
* Currently unused pins

   3V3  (1) (2)  5V    
- GPIO2 PCA9685 SDA (3) (4)  5V    
- GPIO3 PCA9685 SCL (5) (6)  GND   
- GPIO4 IR Control (7) (8)  - GPIO14 UART TX
   GND  (9) (10) - GPIO15 UART RX
* GPIO17 (11) (12) - GPIO18
- GPIO27 (13) (14) GND   
- GPIO22 (15) (16) - GPIO23
   3V3 (17) (18) - GPIO24
* GPIO10 SPI (19) (20) GND   
* GPIO9 SPI (21) (22) - GPIO25
* GPIO11 SPI (23) (24) * GPIO8 SPI0 CE0
   GND (25) (26) * GPIO7 SPI0 CE1
- GPIO0 (27) EEPROM SDA (28) - GPIO1 EEPROM SCL | CAT24C32: EEPROM 串行 32-Kb I2C
- GPIO5 (29) (30) GND   
- GPIO6 (31) (32) - GPIO12
- GPIO13 (33) (34) GND   
- GPIO19 (35) (36) - GPIO16
- GPIO26 (37) (38) - GPIO20
   GND (39) (40) - GPIO21

'''

RUNNING = True

# TODO: assign a pin to sos 

SPEED = 40 # controls vehicle speed
TIME = 0.2
ENABLE_BUTTON = True # onboard yellow cap switch
ENABLE_SONIC2 = True # 超声2 and BACK Collision share GPIO 13 and 26

# 四轮驱动

PWMA   = 18
AIN1   = 22
AIN2   = 27

PWMB   = 23
BIN1   = 25
BIN2   = 24

# 开关及LED

BtnPin  = 19 # Use this button to start/stop program 

colors = [0x010000, 0x001000] 

# 超声

TRIG = 20
ECHO = 21

# 超声2

TRIG2 = 13
ECHO2 = 26

# Fall detection. Use the three bottom tracking sensors. 
# BOTTOM_RIGHT = 26 # change to back collision sensor
BOTTOM_MIDDLE = 19 # use the yellow cap to swtich between button or this sensor
# BOTTOM_LEFT  = 13 # change to back collision sensor

# Collision detection with IR
SHORT_RANGE_RIGHT = 16 # weird, sometimes return True even if not colliding
SHORT_RANGE_LEFT  = 12
SHORT_RANGE_BACK_RIGHT = 26
SHORT_RANGE_BACK_LEFT  = 13

USED_PINS = [PWMA, AIN1, AIN2, PWMB, BIN1, BIN2, BtnPin, 5, 6, TRIG, ECHO, BOTTOM_MIDDLE, 
SHORT_RANGE_BACK_LEFT, SHORT_RANGE_BACK_RIGHT, SHORT_RANGE_LEFT, SHORT_RANGE_RIGHT]
USED_PINS.sort()

def print_used_pins():
    import os
    os.system('pinout')
    print (USED_PINS)
  
def t_up(speed = SPEED,t_time = TIME):

    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN2,False)#AIN2
    GPIO.output(AIN1,True) #AIN1

    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2,False)#BIN2
    GPIO.output(BIN1,True) #BIN1
    time.sleep(t_time)

    #near_verge = fall_detection()
    #if (near_verge):
    #    t_down(SPEED, 0.5)
    #    # SOS or buzz
    #    destroy('fall_detection')
        
def t_stop(t_time = TIME):

    L_Motor.ChangeDutyCycle(0)
    GPIO.output(AIN2,False)#AIN2
    GPIO.output(AIN1,False) #AIN1

    R_Motor.ChangeDutyCycle(0)
    GPIO.output(BIN2,False)#BIN2
    GPIO.output(BIN1,False) #BIN1
    time.sleep(t_time)
        
def t_down(speed = SPEED,t_time = TIME):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN2,True)#AIN2
    GPIO.output(AIN1,False) #AIN1

    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2,True)#BIN2
    GPIO.output(BIN1,False) #BIN1
    time.sleep(t_time)

def t_left(speed = SPEED,t_time = TIME):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN2,True)#AIN2
    GPIO.output(AIN1,False) #AIN1

    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2,False)#BIN2
    GPIO.output(BIN1,True) #BIN1
    time.sleep(t_time)

def t_right(speed = SPEED,t_time = TIME):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN2,False)#AIN2
    GPIO.output(AIN1,True) #AIN1

    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2,True)#BIN2
    GPIO.output(BIN1,False) #BIN1
    time.sleep(t_time)
        
def keyscan():

    val = GPIO.input(BtnPin)
    while GPIO.input(BtnPin) == False:  # wait for press       
        # val = GPIO.input(BtnPin)
        print('front detection: ', front_detection())
        # print('back detection: ', back_detection())

    time.sleep(0.1) # after start, set green light on and red off

    # another press will stop the program
    GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V)
    GPIO.add_event_detect(BtnPin, GPIO.BOTH,
                callback= stop_vehicle,
                bouncetime=200) # TypeError: xxx() takes 0 positional arguments but 1 was given

    return
            
def setup():

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    # # LED
    led.setup()

    # # pbz
    pbz.setup(led.pwm_B) # use the pwm object from led

    # # Servo
    servo.setup()

    # joystick
    joystick.setup()

    # supersonic
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

    # lcd. now can only control backlight, research later
    lcd = LiquidCrystal_I2C()
    lcd.noBacklight()

    if ENABLE_BUTTON:
        GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V)
    else:
        # fall detection or road tracking

        # GPIO.setup(BOTTOM_LEFT,GPIO.IN)
        GPIO.setup(BOTTOM_MIDDLE,GPIO.IN)
        # GPIO.setup(BOTTOM_RIGHT,GPIO.IN)

    # collision detection
    GPIO.setup(SHORT_RANGE_LEFT,GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(SHORT_RANGE_RIGHT,GPIO.IN, pull_up_down=GPIO.PUD_UP)

    if ENABLE_SONIC2 == False:
        GPIO.setup(SHORT_RANGE_BACK_LEFT,GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(SHORT_RANGE_BACK_RIGHT,GPIO.IN, pull_up_down=GPIO.PUD_UP)
    else:
        GPIO.setup(TRIG2, GPIO.OUT)
        GPIO.setup(ECHO2, GPIO.IN)
    
    GPIO.setup(AIN2,GPIO.OUT)
    GPIO.setup(AIN1,GPIO.OUT)
    GPIO.setup(PWMA,GPIO.OUT)
    
    GPIO.setup(BIN1,GPIO.OUT)
    GPIO.setup(BIN2,GPIO.OUT)
    GPIO.setup(PWMB,GPIO.OUT)
    
    global L_Motor, R_Motor 
    L_Motor= GPIO.PWM(PWMA,100)
    L_Motor.start(0)
    R_Motor = GPIO.PWM(PWMB,100)
    R_Motor.start(0)
    
    # # test fall and collision
    # print( fall_detection() )
    # print( collision_detection() )    
    print_used_pins()

def distance(pin_trig = TRIG, pin_echo = ECHO):

    GPIO.output(pin_trig, 0)
    time.sleep(0.000002)
    GPIO.output(pin_trig, 1)
    time.sleep(0.00001)
    GPIO.output(pin_trig, 0)
    
    while GPIO.input(pin_echo) == 0:
        a = 0
    time1 = time.time()
    while GPIO.input(pin_echo) == 1:
        a = 1
    time2 = time.time()

    during = time2 - time1
    return during * 340 / 2 * 100

def front_detection():

    servo.turn_direction(0,90)
    time.sleep(0.5)
    dis_f = distance()
    return dis_f

def back_detection():

    servo.turn_direction(3,90)
    time.sleep(0.5)
    dis_b = distance(TRIG2, ECHO2) # need to wire ultrsound
    return dis_b

def left_detection():
    servo.turn_direction(0, 170)
    time.sleep(0.5)
    dis_l = distance()
    return dis_l
        
def right_detection():
    servo.turn_direction(0, 10)
    time.sleep(0.5)
    dis_r = distance()
    return dis_r

def fall_detection(verbose = False):
    '''
    To sensative. A small bump will trigger.
    '''

    # BL = GPIO.input(BOTTOM_LEFT)
    BM = GPIO.input(BOTTOM_MIDDLE)
    # BR = GPIO.input(BOTTOM_RIGHT)
    # B = BL or BM or BR # means it is empty downside, i.e., on a cliff verge
    
    if verbose:
        print('fall detectection: ', BM)
    
    return BM

def collision_detection(disable_back_sensors = True, verbose = False):

    c_left, c_right = not GPIO.input(SHORT_RANGE_LEFT), not GPIO.input(SHORT_RANGE_RIGHT) # right seems opposite # these two sensors are in the front
    
    if ENABLE_SONIC2:
        c_back_left, c_back_right = False, False 
    else:
        c_back_left, c_back_right = not GPIO.input(SHORT_RANGE_BACK_LEFT), not GPIO.input(SHORT_RANGE_BACK_RIGHT) # these two sensors are in the back

    if verbose:
        print('collision detection: ', c_left, c_right, c_back_left, c_back_right)
    
    return c_left, c_right, c_back_left, c_back_right

def loop():
    
    if ENABLE_BUTTON:
        keyscan()

    while True:

        while not RUNNING:
            t_stop(0)
            time.sleep(0.5)

        if True:
            near_verge = False # the current fall detection is too sensative, turn it off
            # near_verge ,_,_,_ = fall_detection()
            
            c_left, c_right, c_back_left, c_back_right = collision_detection(verbose = False)
            # c_back_left, c_back_right = False, False
            if (c_left and not c_right) or (c_back_left and not c_back_right):
                print('C L > R', c_left, c_right, c_back_left, c_back_right)
                t_right(SPEED,0)
            elif (not c_left and c_right) or (not c_back_left and c_back_right):
                print('C L < R', c_left, c_right, c_back_left, c_back_right)
                t_left(SPEED,0)
            elif c_left and c_right:
                print('C LR', c_left, c_right, c_back_left, c_back_right)
                t_stop(0.1)
                t_down(SPEED, 0.5)
            elif c_back_left and c_back_right:
                print('C BLR', c_left, c_right, c_back_left, c_back_right)
                t_stop(0.1)
                t_up(SPEED, 0.3)

        distance_F = front_detection()

        if distance_F < 40: # or near_verge or c_left or c_right or c_back_left or c_back_right:
            t_stop(0.2)
            t_down(SPEED,0.2)
            t_stop(0.2)

            distance_L = left_detection()
            distance_R = right_detection()
            
            if (distance_L < 40) == True and (distance_R < 40) == True:
                print('US LR < 40', distance_L, distance_R)
                t_left(SPEED,1)
            elif (distance_L > distance_R) == True:
                print('US L > R', distance_L, distance_R)
                t_left(SPEED,0.3)
                t_stop(0.1)
            else:
                print('US L < R', distance_L, distance_R)
                t_right(SPEED,0.3)
                t_stop(0.1)
        else:
            t_up(SPEED,0)           
        
        
        ################### The tracking band function #################

        if False:
            _, SL, _, SR = fall_detection()
            if SL == False and SR == False:
                print ("Up")
                t_up(50,0)
            elif SL == True and SR ==False:
                print ("Left")
                t_left(50,0)
            elif SL==False and SR ==True:
                print ("Right")
                t_right(50,0)
            else:
                t_stop(0)

def stop_vehicle(ch):
    print('Stop Vehicle by ' , ch)
    # L_Motor.stop()
    # R_Motor.stop()
    t_stop(2)

def destroy(ch):
    print('Destroy by' , ch)
    GPIO.cleanup()

if __name__ == "__main__":
    
    setup()   

    try:
        loop()
    except KeyboardInterrupt:
        destroy('keyboard')
