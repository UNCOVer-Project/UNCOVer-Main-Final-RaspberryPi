import os
# Import playsound as a library to play sound in Raspberry
from util import playSound


os.putenv('SDL_AUDIODRIVER', 'alsa')
os.putenv('SDL_AUDIODEV', '/dev/audio')
playSound('speech.mp3')