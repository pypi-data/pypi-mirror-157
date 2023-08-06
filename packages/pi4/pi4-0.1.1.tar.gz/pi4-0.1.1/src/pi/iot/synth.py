import pyttsx3

engine = pyttsx3.init() # object creation

""" RATE"""
rate = engine.getProperty('rate')   # getting details of current speaking rate
print (rate)                        #printing current voice rate
engine.setProperty('rate', 200)     # setting up new voice rate


"""VOLUME"""
volume = engine.getProperty('volume')   #getting to know current volume level (min=0 and max=1)
print (volume)                          #printing current volume level
engine.setProperty('volume',1.0)    # setting up volume level  between 0 and 1

"""VOICE"""
voices = engine.getProperty('voices')       #getting details of current voice
#engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male
engine.setProperty('voice', voices[1].id)   #changing index, changes voices. 1 for female

engine.say("Shall I wither and fall like an autumn leaf, \
From this deep sorrow - from this painful grief? \
How can I go on or find a way to be strong? \
Will I ever again enjoy life's sweet song? \
")

engine.say('My current speaking rate is ' + str(rate))
engine.runAndWait()
engine.stop()


"""Saving Voice to a file"""
# On linux make sure that 'espeak' and 'ffmpeg' are installed
# engine.save_to_file('Hello World', 'test.mp3')
engine.runAndWait()


