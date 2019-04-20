# Libs for text-to-speech
# import os
import requests
from xml.etree import ElementTree

# Libs to play sound
from playsound import playsound

# Libs to get Image Size
from PIL import Image


def getImageSize(image_path):
    '''
        function to get image width and height dimension

        @param image_path: Set image_path to the local path
            of an image that you want to analyze.
    '''
    im = Image.open(image_path)
    width, height = im.size

    return (width, height)


def playSound(filepath):
    playsound(filepath)


class ObjectDetection(object):
    def __init__(self, subscription_key, image_path):
        self.subscription_key = subscription_key
        self.image_path = image_path

    def DetectObject(self):
        '''
        Azure Computer Vision API

        @param image_path: Set image_path to the local path
            of an image that you want
        to analyze.
        '''
        print(
            'LOG: Commencing image recognition of '
            + self.image_path + '\nusing Azure Computer Vision API...'
        )

        subscription_key = self.subscription_key

        print('LOG: Using vision subscription_key ' + subscription_key)

        assert subscription_key

        vision_base_url = ("https://southeastasia.api.cognitive.microsoft.com/"
                           + "vision/v2.0/")

        print('LOG: Using vision base url ' + vision_base_url)

        analyze_url = vision_base_url + "detect"

        print('LOG: Reading the image into a byte array...')

        # Read the image into a byte array
        image_data = open(self.image_path, "rb").read()

        headers = {'Ocp-Apim-Subscription-Key': subscription_key,
                   'Content-Type': 'application/octet-stream'}
        params = {'visualFeatures': 'Categories,Description,Color'}
        response = requests.post(
            analyze_url, headers=headers, params=params, data=image_data)
        response.raise_for_status()

        print('LOG: Receiving JSON response...')

        self.result = response.json()

        print('LOG: JSON response received...')

    def getDetectedObject(self):
        result = self.result

        objects_detected = []
        # parse object names from JSON response
        print('LOG: Parsing object names from JSON...')
        for dicts in result['objects']:
            object_name = dicts['object']
            object_pos = []
            for i in dicts['rectangle']:
                object_pos.append(dicts['rectangle'][i])

            objects_detected.append((object_name, object_pos))

        return objects_detected


class TextToSpeech(object):
    def __init__(self, subscription_key, text_candidate):
        '''
        constructor for TextToSpeech object

        :param subscription_key: change to tts subscription_key
        :param text_candidate: text/string to be converted to speech audio file
        '''
        print('LOG: Initializing TextToSpeech object...')
        print('LOG: Using speech subscription_key ' + subscription_key)

        self.subscription_key = subscription_key

        self.tts = text_candidate

        print('LOG: Speech output: ' + text_candidate)

        self.access_token = None

    def get_token(self):
        print('LOG: Getting token...')

        fetch_token_url = ("https://southeastasia.api.cognitive.microsoft.com"
                           + "/sts/v1.0/issueToken")

        print('LOG: Fetching token at ' + fetch_token_url)

        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        response = requests.post(fetch_token_url, headers=headers)
        self.access_token = str(response.text)

    def save_audio(self, filename, quality=0):
        '''
        function to save the generated speech as .wav audio file

        Keyword arguments:
        :param str filename: the name of audio file without extension
        :param int quality: the quality of the audio [0|1]
        '''

        qual = (
            'audio-24khz-48kbitrate-mono-mp3',
            'riff-16khz-16bit-mono-pcm',
            'riff-24khz-16bit-mono-pcm'

        )

        extension = '.wav'
        if quality == 0:
            extension = '.mp3'

        print('LOG: Processing audio...')

        base_url = 'https://southeastasia.tts.speech.microsoft.com/'

        print('LOG: Using speech base url ' + base_url)

        path = 'cognitiveservices/v1'
        constructed_url = base_url + path
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': qual[quality],
            'User-Agent': 'YOUR_RESOURCE_NAME'
        }
        xml_body = ElementTree.Element('speak', version='1.0')
        xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-us')
        voice = ElementTree.SubElement(xml_body, 'voice')
        voice.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-US')
        voice.set(
            'name',
            'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
        )
        voice.text = self.tts
        body = ElementTree.tostring(xml_body)

        response = requests.post(constructed_url, headers=headers, data=body)
        if response.status_code == 200:
            print('LOG: Saving audio as ' + filename + '...')

            with open(filename + extension, 'wb') as audio:
                audio.write(response.content)
                print(
                    "\nStatus code: "
                    + str(response.status_code)
                    + "\nYour TTS is ready for playback.\n"
                )

        else:
            print(
                "\nStatus code: "
                + str(response.status_code)
                + "\nSomething went wrong. "
                + "Check your subscription key and headers.\n"
            )


class FingerDetection(object):
    def __init__(self, prediction_key, image_path):
        self.prediction_key = prediction_key
        self.image_path = image_path

    def PredictImage(self):
        # req_url = (
        #     'https://southeastasia.api.cognitive.microsoft.com/' +
        #     'customvision/v1.1/Prediction/{}/image/nostore'.format(
        #         self.project_id
        #     )
        # )
        req_url = (
            "https://southeastasia.api.cognitive.microsoft.com/"
            + "customvision/v3.0/Prediction/"
            + "47917e0f-ee76-4fc3-afe4-1eb02b94d6b0/"
            + "detect/iterations/Iteration7/image/nostore"
        )

        image_data = open(self.image_path, 'rb').read()

        headers = {'Content-Type': 'application/octet-stream',
                   'Prediction-key': self.prediction_key}

        response = requests.post(
            req_url,
            headers=headers,
            data=image_data
        )

        response.raise_for_status()

        self.result = response.json()

    def getPrediction(self, minProb=0):
        result = self.result
        detected = []
        # # parse object names from JSON response
        for dicts in result['predictions']:
            prob = dicts['probability']

            if prob < minProb:
                continue

            name = dicts['tagName']
            pos = []
            for i in dicts['boundingBox']:
                pos.append(dicts['boundingBox'][i])

            detected.append((name, pos))

        return detected

    def getPredictionJson(self):
        result = self.result
        return result


class OCR(object):
    def __init__(self, sub_key, img_path):
        self.sub_key = sub_key
        self.img_path = img_path

    def PerformOCR(self):
        assert self.sub_key

        vision_base_url = ("https://southeastasia.api.cognitive.microsoft.com/"
                           + "vision/v2.0/")

        ocr_url = vision_base_url + "ocr"

        # Read the image into a byte array
        image_data = open(self.img_path, "rb").read()

        headers = {'Ocp-Apim-Subscription-Key': self.sub_key,
                   'Content-Type': 'application/octet-stream'}
        params = {'language': 'unk', 'detectOrientation': 'true'}
        response = requests.post(
            ocr_url, headers=headers, params=params, data=image_data)
        response.raise_for_status()

        self.result = response.json()

    def GetTexts(self):
        text = ''

        for i in self.result['regions']:
            for j in i['lines']:
                for k in j['words']:
                    # print(k['text'], end=' ')
                    text += (k['text'] + ' ')
                text += '. '

        return text


class Describe(object):
    def __init__(self, sub_key, img_path):
        self.sub_key = sub_key
        self.img_path = img_path

    def DescribeImage(self):
        assert self.sub_key

        vision_base_url = ("https://southeastasia.api.cognitive.microsoft.com/"
                           + "vision/v2.0/")

        desc_url = vision_base_url + "describe"

        # Read the image into a byte array
        image_data = open(self.img_path, "rb").read()

        headers = {'Ocp-Apim-Subscription-Key': self.sub_key,
                   'Content-Type': 'application/octet-stream'}
        params = {'maxCandidates': '1', 'language': 'en'}
        response = requests.post(
            desc_url, headers=headers, params=params, data=image_data)
        response.raise_for_status()

        self.result = response.json()

    def GetDescription(self):
        res = self.result

        try:
            return res['description']['captions'][0]['text']
        except IndexError:
            return 'There are no description for the scene'


class Analyze(object):
    def __init__(self, sub_key, img_path):
        self.sub_key = sub_key
        self.img_path = img_path

    def AnalyzeImage(self):
        assert self.sub_key

        vision_base_url = ("https://southeastasia.api.cognitive.microsoft.com/"
                           + "vision/v2.0/")

        analyze_url = vision_base_url + "analyze"
        visualFeatures = (
            'Brands,Color,Description,Faces'
        )

        # Read the image into a byte array
        image_data = open(self.img_path, "rb").read()

        headers = {'Ocp-Apim-Subscription-Key': self.sub_key,
                   'Content-Type': 'application/octet-stream'}
        params = {'visualFeatures': visualFeatures,
                  'details': 'Celebrities,Landmarks'}
        response = requests.post(
            analyze_url, headers=headers, params=params, data=image_data)
        response.raise_for_status()

        self.result = response.json()

    def GetResult(self):
        '''
        Get analyze result

        :return (colors[], brands[], desc, faces[(age, gender)]):
        '''
        res = self.result

        colors = []
        for color in res['color']['dominantColors']:
            colors.append(color)

        brands = []
        for brand in res['brands']:
            brands.append(brand['name'])

        desc = res['description']['captions'][0]['text']

        faces = []
        for face in res['faces']:
            faces.append((face['age'], face['gender']))

        return ((colors, brands, desc, faces))

