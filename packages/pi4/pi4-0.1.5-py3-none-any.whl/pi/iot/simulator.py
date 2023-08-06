class GPIO:

    LOW = 0 
    HIGH = 1
    OUT = 2
    IN = 3
    PUD_OFF = 4
    PUD_DOWN = 5
    PUD_UP = 6
    BCM = 7
    BOARD = 10

    def setwarnings(flags):
        pass

    def setmode(mode):
        pass

    def setup(channel, state, initial=None, pull_up_down=None):
        pass

    def output(channel, value):
        pass

    def input(channel):
        pass

    def wait_for_edge(channel, edge):
        pass

    def PWM(channel, frequency):
        return PWM(channel, frequency)

    def cleanup():
        pass

    def add_event_detect(pin, mode,
                callback,
                bouncetime):
        pass

class PWM:

    def __init__(self, channel, freq):
        pass

    def start(self, dc):
        pass

    def stop(self):
        pass

    def ChangeDutyCycle(self, dc):
        pass

    def ChangeFrequency(self, freq):
        pass    

class SMBus:
    
    def __init__(self, ver):
        pass

    def write_byte_data(self, address, reg, value):
        pass

    def read_byte_data(self, address, reg):
        return 0x00

class pylirc:
    
    def init(a = "pylirc", b = "./conf", c = None):
        pass

    def nextcode(i):
        pass

    def exit():
        pass

    