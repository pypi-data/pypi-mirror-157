import sys
import os.path
if sys.platform == 'win32' or not __package__:
    sys.path.append(os.path.dirname(__file__))
    from simulator import GPIO
else:
	from RPi import GPIO

import time

RUNNING = True

# control intensity
colors = [0x880000, 0x00ff00, 0x000088] #  0xFFFF00, 0xFF00FF, 0x00FFFF, 

# 初始化程序
def setup(Rpin = 5, Gpin = 6, Bpin = 18): # 17, 18, 27 - 11, 12, 13
	global pins
	global p_R, p_G, p_B
	pins = {'pin_R': Rpin, 'pin_G': Gpin, 'pin_B': Bpin}
	GPIO.setmode(GPIO.BCM)        # 采用实际的物理管脚给GPIO口
	GPIO.setwarnings(False)         # 去除GPIO口警告
	for i in pins:
		GPIO.setup(pins[i], GPIO.OUT)   # 设置Pin模式为输出模式
		GPIO.output(pins[i], GPIO.LOW)  # 设置Pin管脚为低电平(0V)关闭LED

    # control blink freq
	# 由于RGB三色模块每一个LED达到一定的亮度，需要的电流值是不一样，所以设置的频率有区别
	p_R = GPIO.PWM(pins['pin_R'], 30)  # 设置频率为 n Hz
	p_G = GPIO.PWM(pins['pin_G'], 30)
	p_B = GPIO.PWM(pins['pin_B'], 30)
	
	# 初始化占空比为0(led关闭)
	p_R.start(0)
	p_G.start(0)
	p_B.start(0)

# 关闭RGB-LED灯
def off():
	for i in pins:
		GPIO.setup(pins[i], GPIO.OUT)     # 设置Pin模式为输出模式
		GPIO.output(pins[i], GPIO.LOW)    #  设置Pin管脚为低电平(0V)关闭LED

# 设置颜色
def set_Color(col):   #  例如:col  = 0x112233
	R_val = int ( ((col & 0xff0000) >> 16) / 2.56 )
	G_val = int ( ((col & 0x00ff00) >> 8) / 2.56 )
	B_val = int ( ((col & 0x0000ff) >> 0) / 2.56 )

	# dutycycle must have a value from 0.0 to 100.0
	# print(R_val, G_val, B_val)
	
	p_R.ChangeDutyCycle(R_val)     # 改变占空比, intensity
	p_G.ChangeDutyCycle(G_val)     # 改变占空比
	p_B.ChangeDutyCycle(B_val)     # 改变占空比

# 循环函数
def loop():
	while RUNNING:
		for col in colors:
			set_Color(col)  # 设置颜色
			time.sleep(0.5)            # 延时1s. time interval between color change
# 资源释放
def destroy():
	p_R.stop()      # 关闭红色PWM
	p_G.stop()      # 关闭绿色PWM
	p_B.stop()      # 关闭蓝色PWM
	off()  # 关闭RGB-LED灯
	GPIO.cleanup()  # 释放资源

# 程序入口
if __name__ == "__main__":
	try:
		setup() # 初始化设置函数
		loop()                                    # 循环函数
	except KeyboardInterrupt:                              # 当按下Ctrl+C时，将执行destroy()子程序。
		destroy()                                 # 资源释放