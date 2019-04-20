import os
from util import playSound

# for setting audio purposes
# putenv is used to modify the environment 
# using alsa advanced linux sound architecture
os.putenv('SDL_AUDIODRIVER', 'alsa')
os.putenv('SDL_AUDIODEV', '/dev/audio')
playSound('speech.mp3')