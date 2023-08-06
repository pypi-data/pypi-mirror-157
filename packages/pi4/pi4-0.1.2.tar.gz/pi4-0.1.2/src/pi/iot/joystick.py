if __package__:
	from . import PCF8591 as ADC
else:
	import PCF8591 as ADC
import time

RUNNING = True
HANDLER = print

# 初始化
def setup():

	ADC.setup(ADC.I2C_ADC) # 设置PCF8591模块地址
	
	global STATUS            # 状态变量
	STATUS = ['', 'up3x', 'up2x', 'up1x', \
	'down3x', 'down2x', 'down1x', \
	'left3x', 'left2x', 'left1x', \
	'right3x', 'right2x', 'right1x', \
	'pressed' ]  # 方向状态信息

# 方向判断函数
def navigate():	
	
	i = 0
	UD = ADC.read(1)

	if UD <= 30:
		i = 1		# up方向 3x
	elif UD <= 70:
		i = 2
	elif UD <= 110:
		i = 3

	if UD >= 225:
		i = 4		# down方向 3x
	elif UD >= 185:
		i = 5
	elif UD >= 145:
		i = 6

	LR = ADC.read(2)

	if LR >= 225:
		i = 7		# left方向 3x
	elif LR >= 185:
		i = 8
	elif LR >= 145:
		i = 9

	if LR <= 30:
		i = 10		# right方向 3x
	elif LR <= 70:
		i = 11
	elif LR <= 110:
		i = 12

	BTN = ADC.read(3)
	if BTN == 0: # or BTN == 128:
		i = 13		# Button按下
    
	# N/A status
	if abs(UD - 127) < 15 and abs(LR - 127) <15 and BTN == 255:
		i = 0

	return STATUS[i] 

# 循环函数
def loop():
	status = ''

	while RUNNING:
		time.sleep(0.1)
		tmp = navigate()   # 调用方向判断函数
		if tmp != None and tmp != status:  # 判断状态是否发生改变
			status = tmp # 把当前状态赋给状态值，以防止同一状态多次打印
			if HANDLER:
				HANDLER (status) # a callback function
			# print( ADC.read(1), ADC.read(2), ADC.read(3) ) # 打印出方向位 and all the inputs

# 异常处理函数
def destroy():
	pass

# 程序入口
if __name__ == '__main__':		
	
	setup()  # 初始化
	try:
		loop() # 调用循环函数
	except KeyboardInterrupt:  	# 当按下Ctrl+C时，将执行destroy()子程序。
		destroy()   # 调用释放函数