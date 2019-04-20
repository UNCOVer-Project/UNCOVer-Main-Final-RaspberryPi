from posutil import findObjectLocation as findObLoc
from util import ObjectDetection
from util import getImageSize
from util import TextToSpeech
from util import playSound
from util import OCR
from util import FingerDetection
from posutil import findObjectLocation
from posutil import findClosestObjectFromFinger
from posutil import getFingersMiddlePos
from util import Describe
from util import Analyze
import sys
from picamera import PiCamera
from time import sleep
from SpeechRecognition import SpeechRecognition

# build camera instance
cam = PiCamera()


def playErrorSnd(errNo):
    '''
        function to play error sound according to each error code

        Keyword arguments:
        :param int errorNumber to determine which error audio should be played
        
    '''
    soundDir = 'sounds/'
    errSound = soundDir + 'err{}.mp3'.format(errNo)

    playSound(errSound)

   
def imageCapture():
    '''
        function to get image when the user ask, [for debugging purposes also display image captured in screen]
        using PiCamera
        captured image then is sent to AZURE for further process

    '''
    cam.resolution = (2560, 1920)
    # display current recording into screen for debugging purposes
    cam.start_preview()
    # time for user to aim the UNCOVer to desired scene
    sleep(2)
    cam.capture('capture/image.jpg')
    cam.stop_preview()
    return 'capture/image.jpg'
    

def ModeCommand():
    '''
        function to decide what user wants by voice command
        listening to user by speech_recognition then get the string of user's command
        the string command then being checked to certain keyword for each UNCOVer mode
        command divided unto 2 category: main-command and sub-command

        there are 2 main command:
        1. turn off                 turning off the UNCOVer
        2. uncover                  start listening for further sub-command
        
        4 sub-command(mode) for main-comman "uncover":

        Mode's code and name:
        # 0 -> object positions     (output object's name and position (left, center, right) by speech)
        # 1 -> pointed object       (using custom vision to detect finger and output the pointed object by speech)
        # 2 -> OCR                  (read and speak out the text from the image)
        # 3 -> image analysis       (analyze image using AZURE vision and output the scene description result by speech)
        # 4 -> describe image       (describe image using AZURE vision by speech including dominant color, people's age and gender, brand, and description)

    '''

    sr1 = SpeechRecognition()
    listen = sr1.recognize()

    print(1, listen.lower())
    # decide which command is asked
    if "turn off" in listen.lower():
        sys.exit(0)

    elif "uncover" in listen.lower():

        sr2 = SpeechRecognition()
        playSound('sounds/notification.wav')
        listen = sr2.recognize()
        print(2, listen.lower())

        # each mode must-included-keyword's
        # if the user command contain all such keyword then such operation mode is activated
        com0 = ['what', 'front']
        com1 = ['what', 'point']
        com2 = ['text', 'read']
        com3 = 'analyze'
        com4 = 'describe'
        
        # count the number of valid keyword included
        ctr = 0
        for i in com0:
            if i in listen.lower():
                ctr += 1
        if ctr == 2:
            return '0'
        
        ctr = 0
        for i in com1:
            if i in listen.lower():
                ctr += 1
        if ctr == 2:
            return '1'
        
        ctr = 0
        for i in com2:
            if i in listen.lower():
                ctr += 1
        if ctr == 2:
            return '2'
        
        if com3 in listen.lower():
            return '3'
        
        if com4 in listen.lower():
            return '4'
        else:
            # sub-command not detected, start for listening to main command
            return '-1'
    else:
        # main command are not detected
        return '-2'
            

# each error code for sound error file
PREM_NO_OBJ_DETECT = 0
PREM_NO_FING_DETECT = 1
PREM_NO_TEXT_DETECT = 2

while True:
    # get what operation should be activated by listening to user's command
    mode = ModeCommand()
    
    imageFile = ''

    if mode == '-1':
        # if main-command not detected (not containing 'turn off' or 'uncover')
        playSound('sounds/notification.wav')
        continue
    elif mode == '-2':
        # if sub-command not detected
        playSound('sounds/wrong.wav')
        continue
    
    # AZURE API SubscriptionKey
    visionSubKey = 'f21b4f194bb1480c8dde294d9baf18e7'
    ttsSubKey = 'd7f48f6fc6d34d6bae9b72814bbd0519'
    
    # get the image from camera
    imageFile = imageCapture()


    if mode == '0':
        # activate UNCOVer's ObjectLocation operation mode
        objectDetect = ObjectDetection(visionSubKey, imageFile)
        objectDetect.DetectObject()
        # obtain object location from AZURE
        objects = objectDetect.getDetectedObject()

        objectLoc = findObLoc(objects, getImageSize(imageFile))

        if objectLoc == []:
            playErrorSnd(PREM_NO_OBJ_DETECT)
            continue
            
        else:
            centerObj = []
            leftObj = []
            rightObj = []
            # parse output to the spoken-string
            for name, loc in objectLoc:
                if loc == 'center':
                    centerObj.append(name)
                elif loc == 'left':
                    leftObj.append(name)
                else:
                    rightObj.append(name)

            textCand = ''
            lenLeftObj = len(leftObj)
            lenCenterObj = len(centerObj)
            lenRightObj = len(rightObj)

            if lenLeftObj != 0:
                textCand += 'In your left, there '
                if lenCenterObj < 1:
                    textCand += 'are '
                else:
                    textCand += 'is '
                for name in leftObj:
                    textCand += (name + ', ')
                textCand += '. '

            if lenCenterObj != 0:
                textCand += ' Directly in your front of you, there '
                if lenCenterObj < 1:
                    textCand += 'are '
                else:
                    textCand += 'is '
                for name in centerObj:
                    textCand += (name + ', ')
                textCand += '. '

            if lenRightObj != 0:
                textCand += ' In your right, there '
                if lenRightObj < 1:
                    textCand += 'are '
                else:
                    textCand += 'is '
                for name in rightObj:
                    textCand += (name + ', ')
                textCand += '. '

        print(textCand)

        # using AZURE to convert text unto sppech
        tts = TextToSpeech(ttsSubKey, textCand)
        tts.get_token()
        tts.save_audio('speech', 0)

        # play the received audio file from AZURE 
        playSound('speech.mp3')

    elif mode == '1':
        # activate UNCOVer's PointedObject operation mode
        print('Start Initializing Pointed Object Detection')

        # perfrom object detection using AZURE
        objectDetect = ObjectDetection(visionSubKey, imageFile)
        objectDetect.DetectObject()
        objects = objectDetect.getDetectedObject()

        objectLoc = findObLoc(objects, getImageSize(imageFile))

        if objectLoc == []:
            playErrorSnd(PREM_NO_OBJ_DETECT)
            continue
        
        # perform finger detection using AZURE CustomVision
        fingerDetector = FingerDetection(
            '4b0ab4fa945a41b187c5fcb6c4ea5cdb',
            imageFile
        )

        fingerDetector.PredictImage()
        fingerDetected = fingerDetector.getPrediction(0.5)

        fingersMidPos = getFingersMiddlePos(
            fingerDetected, getImageSize(imageFile)
        )

        if fingersMidPos == []:
            playErrorSnd(PREM_NO_FING_DETECT)
            continue
           
        else:
            # find object location relative to the image
            validObjs = findObjectLocation(
                objects, getImageSize(imageFile)
            )

            # find the closest object from finger
            closestObj = findClosestObjectFromFinger(
                objects, fingersMidPos[0], True
            )
            # parse output to the spoken-string
            print('Closest object: ', closestObj)
            pointedText = 'You are pointing at: ' + closestObj[0]

        
        # using AZURE to convert text unto sppech
        tts = TextToSpeech(ttsSubKey, pointedText)
        tts.get_token()
        tts.save_audio('pointedSpeech', 0)
        
        # play the received audio file from AZURE 
        playSound('pointedSpeech.mp3')

    elif mode == '2':
        # activate UNCOVer's OpticalCharacterRecognition operation mode
        print('Start Initializing OCR')
        # perfrom OpticalCharacterRecognition using AZURE
        OCRecognizer = OCR(visionSubKey, imageFile)
        OCRecognizer.PerformOCR()
        
        # parse output to the spoken-string
        OCRText = OCRecognizer.GetTexts()
        print(OCRText)
        if OCRText == "":
            playErrorSnd(PREM_NO_TEXT_DETECT)
        
        # using AZURE to convert text unto sppech
        tts = TextToSpeech(ttsSubKey, OCRText)
        tts.get_token()
        tts.save_audio('ocrspeech', 0)

        # play the received audio file from AZURE 
        playSound('ocrspeech.mp3')

    elif mode == '3':
        # activate UNCOVer's ImageAnalyzation operation mode
        print('Start Initalizing Image Analysis')
        # perfrom ImageAnalyzation using AZURE
        analyzer = Analyze(visionSubKey, imageFile)
        analyzer.AnalyzeImage()
        analyzed = analyzer.GetResult()

        # parse output to the spoken-string 
        analysisText = "Analyzed result: "
        # color, brand, desc, face(age, gender)
        color = analyzed[0]
        brand = analyzed[1]
        desc = analyzed[2]
        face = analyzed[3]


        if(desc != ""):
            analysisText += desc
            analysisText += ". "
        if(color != []):
            analysisText += "dominant colors are "
            for c in color:
                analysisText += c
                analysisText += ", "
            analysisText += " . "
        if(brand != []):
            analysisText += "detected brands are "
            for c in brand:
                analysisText += c
                analysisText += ", "
            analysisText += ". "
        if(face != []):
            analysisText += "There is "
            for age, gender in face:
                analysisText += "a "
                analysisText += str(age)
                analysisText += " years old "
                analysisText += str(gender)
                analysisText += " person. "

        print(analysisText)

        # using AZURE to convert text unto sppech
        tts = TextToSpeech(ttsSubKey, analysisText)
        tts.get_token()
        tts.save_audio('descspee', 0)

        # play the received audio file from AZURE 
        playSound('descspee.mp3')

    elif mode == '4':
        # activate UNCOVer's ImageDescription operation mode
        print('Start Initalizing Image Description')
        # perfrom ImageDescription using AZURE
        desc = Describe(visionSubKey, imageFile)
        desc.DescribeImage()

        # parse output to the spoken-string 
        descriptionText = desc.GetDescription()
        print(descriptionText)

        # using AZURE to convert text unto sppech
        tts = TextToSpeech(ttsSubKey, 'Describe result: ' + descriptionText)
        tts.get_token()
        tts.save_audio('descspeech', 0)

        # play the received audio file from AZURE 
        playSound('descspeech.mp3')
        
    else:
        playSound('sounds/wrong.wav')
