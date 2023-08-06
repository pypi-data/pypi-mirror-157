#	This is a program for Passive Buzzer Module
#		It will play simple songs.
#	You could try to make songs by youselves!
# 
#		Passive buzzer 			   Pi 
#			VCC ----------------- 3.3V
#			GND ------------------ GND
#			SIG ---------------- GPIO 17
#
#---------------------------------------------------

import sys
import os.path
if sys.platform == 'win32' or not __package__:
    sys.path.append(os.path.dirname(__file__))
    from simulator import GPIO
else:
    import RPi.GPIO as GPIO

import time

Buzzer = 17
RUNNING = True

# 音谱定义
Tone_CL = [0, 131, 147, 165, 175, 196, 211, 248]		# 低音符的频率
Tone_CM = [0, 262, 294, 330, 350, 393, 441, 495]		# 中音的频率
Tone_CH = [0, 525, 589, 661, 700, 786, 882, 990]		# 高音符的频率

# 第一首歌音谱
song_1 = [	Tone_CM[3], Tone_CM[5], Tone_CM[6], Tone_CM[3], Tone_CM[2], Tone_CM[3], Tone_CM[5], Tone_CM[6], 
			        Tone_CH[1], Tone_CM[6], Tone_CM[5], Tone_CM[1], Tone_CM[3], Tone_CM[2], Tone_CM[2], Tone_CM[3], 
			        Tone_CM[5], Tone_CM[2], Tone_CM[3], Tone_CM[3], Tone_CL[6], Tone_CL[6], Tone_CL[6], Tone_CM[1],
			        Tone_CM[2], Tone_CM[3], Tone_CM[2], Tone_CL[7], Tone_CL[6], Tone_CM[1], Tone_CL[5]	]
# 第1首歌的节拍，1表示1/8拍
beat_1 = [	1, 1, 3, 1, 1, 3, 1, 1, 			
			        1, 1, 1, 1, 1, 1, 3, 1, 
			        1, 3, 1, 1, 1, 1, 1, 1, 
			        1, 2, 1, 1, 1, 1, 1, 1, 
			        1, 1, 3	]
# 第二首歌音谱
song_2 = [	Tone_CM[1], Tone_CM[1], Tone_CM[1], Tone_CL[5], Tone_CM[3], Tone_CM[3], Tone_CM[3], Tone_CM[1],
			        Tone_CM[1], Tone_CM[3], Tone_CM[5], Tone_CM[5], Tone_CM[4], Tone_CM[3], Tone_CM[2], Tone_CM[2], 
			        Tone_CM[3], Tone_CM[4], Tone_CM[4], Tone_CM[3], Tone_CM[2], Tone_CM[3], Tone_CM[1], Tone_CM[1], 
			        Tone_CM[3], Tone_CM[2], Tone_CL[5], Tone_CL[7], Tone_CM[2], Tone_CM[1]	]

# 第2首歌的节拍，1表示1/8拍
beat_2 = [	1, 1, 2, 2, 1, 1, 2, 2, 			
			        1, 1, 2, 2, 1, 1, 3, 1, 
			        1, 2, 2, 1, 1, 2, 2, 1, 
			        1, 2, 2, 1, 1, 3 ]
# GPIO设置函数
def setup(pwm_Buzz = None):
	'''
	pwm_Buzz : user may pass a pwm object, e.g., LED Bpin reuses the same pin and may have already initialize the PWM object.
	
	This is the passive buzzer setup. To use active buzzer: 
	GPIO.setup(Buzzer, GPIO.OUT)     # 设置有源蜂鸣器管脚为输出模式
	GPIO.output(Buzzer, GPIO.HIGH)   # pull HIGH. LOW to trigger
	'''

	GPIO.setmode(GPIO.BCM)		# 采用实际的物理管脚给GPIO口
	GPIO.setwarnings(False)         # 关闭GPIO警告提示
	GPIO.setup(Buzzer, GPIO.OUT)	# 设置无源蜂鸣器管脚为输出模式

	global Buzz 
		
	if pwm_Buzz is None:
		Buzz = GPIO.PWM(Buzzer, 440) # 设置初始频率为440。
	else:
		Buzz = pwm_Buzz

# 循环函数
def loop():

	Buzz.start(50) # 按50%工作定额启动蜂鸣器引脚。

	while RUNNING:

		# 播放第二首歌音乐...
		for i in range(1, len(song_2)):     # 播放第二首歌
			Buzz.ChangeFrequency(song_2[i]) # 设置歌曲音符的频率
			time.sleep(beat_2[i] * 0.25)     # 延迟一个节拍* 0.5秒的音符
			if RUNNING == False:
				break

		# 播放第一首歌音乐...
		for i in range(1, len(song_1)):     # 播放第一首歌
			Buzz.ChangeFrequency(song_1[i]) # 设置歌曲音符的频率
			time.sleep(beat_1[i] * 0.5)	 # 延迟一个节拍* 0.5秒的音符
			if RUNNING == False:
				break

		time.sleep(1)						# 等待下一首歌。

	Buzz.stop()

# 释放资源函数
def destory():
	Buzz.stop()			    # 停止蜂鸣器
	GPIO.output(Buzzer, 1)		# 设置蜂鸣器管脚为高电平
	GPIO.cleanup()				        # 释放资源

# 程序入口
if __name__ == '__main__':		
	
	setup()

	try:
		loop()
	except KeyboardInterrupt:  	# 当按下Ctrl+C时，将执行destroy()子程序。
		destory()      # 释放资源
