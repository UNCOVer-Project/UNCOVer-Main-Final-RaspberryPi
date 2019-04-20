# Impot PicCamea libary to run in Raspberry py
from picamera import PiCamera
from time import sleep

# Create instance
cam = PiCamera()
def imageCapture():
    # Set the camera resolution , can be adjusted for diffrent camera
    cam.resolution = (2560, 1920)
    cam.start_preview()
    sleep(4)
    
    # Capture image and save it into jpg file so it can be processed later
    cam.capture('capture/image.jpg')
    cam.stop_preview()

    # Return image
    return 'capture/image.jpg'
    
imageCapture()