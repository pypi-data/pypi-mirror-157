import time
import smbus
# pip install pcf8574
from pcf8574 import PCF8574


I2C_LCD = 0x27

pcf = PCF8574(1, I2C_LCD)
print('PCF8574(1, I2C_LCD).port: ', pcf.port)

BUS = smbus.SMBus(1)
time.sleep(1) #wait here to avoid 121 IO Error

def write_word(data):
	global BLEN
	temp = data
	if BLEN == 1:
		temp |= 0x08
	else:
		temp &= 0xF7
	BUS.write_byte(I2C_LCD ,temp)

def send_command(comm):
	# Send bit7-4 firstly
	buf = comm & 0xF0
	buf |= 0x04               # RS = 0, RW = 0, EN = 1
	write_word(buf)
	time.sleep(0.002)
	buf &= 0xFB               # Make EN = 0
	write_word(buf)

	# Send bit3-0 secondly
	buf = (comm & 0x0F) << 4
	buf |= 0x04               # RS = 0, RW = 0, EN = 1
	write_word(buf)
	time.sleep(0.002)
	buf &= 0xFB               # Make EN = 0
	write_word(buf)

def send_data(data):
	# Send bit7-4 firstly
	buf = data & 0xF0
	buf |= 0x05               # RS = 1, RW = 0, EN = 1
	write_word(buf)
	time.sleep(0.002)
	buf &= 0xFB               # Make EN = 0
	write_word(buf)

	# Send bit3-0 secondly
	buf = (data & 0x0F) << 4
	buf |= 0x05               # RS = 1, RW = 0, EN = 1
	write_word(buf)
	time.sleep(0.002)
	buf &= 0xFB               # Make EN = 0
	write_word(buf)

def init(addr, bl):
#	global BUS
#	BUS = smbus.SMBus(1)
	global BLEN
	BLEN = bl
	try:
		send_command(0x33) # Must initialize to 8-line mode at first
		time.sleep(0.005)
		send_command(0x32) # Then initialize to 4-line mode
		time.sleep(0.005)
		send_command(0x28) # 2 Lines & 5*7 dots
		time.sleep(0.005)
		send_command(0x0C) # Enable display without cursor
		time.sleep(0.005)
		send_command(0x01) # Clear Screen
		BUS.write_byte(I2C_LCD, 0x08)
		# BUS.close()
	except:
		return False
	else:
		return True

def clear():
	send_command(0x01) # Clear Screen

def openlight():  # Enable the backlight
	BUS.write_byte(I2C_LCD,0x08)
	BUS.close()

def write(x, y, str):
	if x < 0:
		x = 0
	if x > 15:
		x = 15
	if y <0:
		y = 0
	if y > 1:
		y = 1

	# Move cursor
	addr = 0x80 + 0x40 * y + x
	send_command(addr)

	for chr in str:
		send_data(ord(chr))

if __name__ == '__main__':

	pcf.port[0] = True # controls light off
	time.sleep(2)

	init(I2C_LCD, 1)
	write(4, 0, 'Hello')
	#write(7, 1, 'world!')

	time.sleep(2)
	pcf.port[0] = True

