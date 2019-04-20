from picamera import PiCamera
from time import sleep

cam = PiCamera()
cam.start_preview()
sleep(0.5)
cam.capture('capture/image.jpg')
cam.stop_preview()