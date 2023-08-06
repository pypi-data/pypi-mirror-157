# 说明： DS18B20数字温度传感器实验
# 注意事项：DS18B20有唯一的地址，一般为28-XXXXXX
#####################################################
import os
import time
from os.path import isdir, isfile

ds18b20 = ''  # ds18b20 设备

def setup():
	global ds18b20  # 全局变量
	# 获取 ds18b20 地址
	if isdir('/sys/bus/w1/devices'):
		for i in os.listdir('/sys/bus/w1/devices'):
			if i != 'w1_bus_master1':
				ds18b20 = i       # ds18b20存放在ds18b20地址

# 读取ds18b20地址数据
def read():
	location = '/sys/bus/w1/devices/' + ds18b20 + '/w1_slave' # 保存ds18b20地址信息

	if not isfile(location):
		print(location, 'does not exist.')
		return None

	print(location)
	tfile = open(location)  # 打开ds18b20 
	text = tfile.read()     # 读取到温度值
	tfile.close()                    # 关闭读取
	secondline = text.split("\n")[1] # 格式化处理
	temperaturedata = secondline.split(" ")[9]# 获取温度数据
	temperature = float(temperaturedata[2:])  # 去掉前两位
	temperature = temperature / 1000          # 去掉小数点
	return temperature                        # 返回温度值

# 循环函数	
def loop():
	while True:
		if read() != None:  # 调用读取温度值，如果读到到温度值不为空
			print ("Temperature : %0.3f C" % read()) # 打印温度值
		time.sleep(1)

# 释放资源
def destroy():
	pass

# 程序入口
if __name__ == '__main__':
	try:
		setup()  # 调用初始化程序
		loop()   # 调用循环函数
	except KeyboardInterrupt: # 当按下Ctrl+C时，将执行destroy()子程序。
		destroy()             # 释放资源

