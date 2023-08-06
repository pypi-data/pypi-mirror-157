import sys
import os.path
if sys.platform == 'win32':
    sys.path.append(os.path.dirname(__file__))
    from simulator import GPIO
else:
	from RPi import GPIO
    
import time

Rpin = 5
Gpin = 6
Bpin = 17 # The blue LED pin is also connected to passive buzzer
FREQ = 60
RUNNING = True

def setup():

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(Rpin, GPIO.OUT)   # 设置Pin模式为输出模式
    GPIO.output(Rpin, GPIO.LOW)  # 设置Pin管脚为低电平(0V)关闭LED
    GPIO.setup(Gpin, GPIO.OUT)   # 设置Pin模式为输出模式
    GPIO.output(Gpin, GPIO.LOW)  # 设置Pin管脚为低电平(0V)关闭LED
    GPIO.setup(Bpin, GPIO.OUT)   # 设置Pin模式为输出模式
    GPIO.output(Bpin, GPIO.LOW)  # 设置Pin管脚为低电平(0V)关闭LED

    global pwm_R, pwm_G, pwm_B   
    # control blink freq
    pwm_R = GPIO.PWM(Rpin, FREQ)
    pwm_G = GPIO.PWM(Gpin, FREQ) # Set higher freqency  
    pwm_B = GPIO.PWM(Bpin, FREQ)

	# 初始化占空比为0(led关闭)
    pwm_R.start(0)
    pwm_G.start(0)
    pwm_B.start(0)

def test_led(R_val = 1, G_val = 16, B_val = 16):
    '''
    R_val and G_val should be in the range (0,100)    '''
    
    # Duty cycle is the ratio of time a load or circuit is ON compared to the time the load or circuit is OFF. Duty cycle, sometimes called "duty factor," is expressed as a percentage of ON time. 
    # A 60% duty cycle is a signal that is ON 60% of the time and OFF the other 40%.
    pwm_R.ChangeDutyCycle(R_val)     # 改变占空比
    pwm_G.ChangeDutyCycle(G_val)     # 改变占空比
    pwm_B.ChangeDutyCycle(B_val)

    time.sleep(0.5)


def sos(pin = Bpin):
    '''
    亮200、灭200、亮200、灭200、亮200、灭500、
    亮400、灭200、亮400、灭200、亮400、灭500、
    亮200、灭200、亮200、灭200、亮200、灭1300 （MS）循环 低电平LED亮。

    pin : connect to LED or laser
    '''
    pin_on_off(pin)
    pin_on_off(pin)
    pin_on_off(pin, t2=0.5)
    pin_on_off(pin, t1=0.4)
    pin_on_off(pin, t1=0.4)
    pin_on_off(pin, 0.4,0.5)
    pin_on_off(pin)
    pin_on_off(pin)
    pin_on_off(pin, t2=1.3)

    print('one episode finished')

def pin_on_off(pin, t1 = 0.2, t2 = 0.2):
    # 打开激光传感器
    GPIO.output(pin, GPIO.HIGH)  # 打开激光传感器
    time.sleep(t1)
    # 关闭激光传感器
    GPIO.output(pin, GPIO.LOW) # 关闭激光传感器
    time.sleep(t2)

def loop():

    while RUNNING: # modify the RUNNING var in outer app to control running
        test_led(R_val = 40, G_val = 0, B_val = 0)
        test_led(R_val = 0, G_val = 70, B_val =0)
        test_led(R_val = 0, G_val = 0, B_val = 90)
    
    test_led(0,0,0)
    
	# destroy()
	# raise Exception('Terminate') # raise exception to terminate the thread

def destroy():
	pwm_R.stop()      # 关闭红色PWM
	pwm_G.stop()      # 关闭绿色PWM
	pwm_B.stop()      # 关闭绿色PWM    

	GPIO.output(Rpin, GPIO.LOW)  
	GPIO.output(Gpin, GPIO.LOW)  
	GPIO.output(Bpin, GPIO.LOW)  

	GPIO.cleanup()  # 释放资源

if __name__ == "__main__":
	try:
		setup()
		loop()                               
	except KeyboardInterrupt:                             
		destroy()