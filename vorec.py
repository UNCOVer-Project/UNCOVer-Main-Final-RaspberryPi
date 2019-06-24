import os
from util import playSound

# For setting audio purposes
# Putenv is used to modify the environment 
# Using alsa advanced linux sound architecture
os.putenv('SDL_AUDIODRIVER', 'alsa')
os.putenv('SDL_AUDIODEV', '/dev/audio')
playSound('speech.mp3')
