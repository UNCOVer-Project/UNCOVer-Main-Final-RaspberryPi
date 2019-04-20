import speech_recognition as sr


class SpeechRecognition:
    """
    Speech recognition using SpeechRecognition
    https://github.com/Uberi/speech_recognition

    Specifically used for Azure Speech API

    Example usage:
        text = SpeechRecognition().recognize()
        print(text)
    """

    def __init__(self, token_key='d7f48f6fc6d34d6bae9b72814bbd0519'):
        """Initialize self. If no token key is provided,
        the default one will be used (may not be valid after sometime)

        :param token_key: Azure Speech subscription key
        """
        self.token_key = token_key

    def recognize(self, device_index=-1):
        """Start recognizing. If device index is not provided,
        default microphone will be used

        To list device indexes, run:
        sr.Microphone.list_microphone_names()

        :param device_index: The device id of microphone
        """

        r = sr.Recognizer()
        if device_index == -1:
            mic = sr.Microphone()
        else:
            mic = sr.Microphone(device_index=device_index)

        with mic as source:
            print('Please silent...')
            r.adjust_for_ambient_noise(source)
            print('Recording...')
            audio = r.listen(source)

        print('Done recording...')
        text = ''
        try:
            text = r.recognize_azure(
                audio, self.token_key, location='southeastasia'
            )
        except sr.UnknownValueError:
            print('The voice is not recognizable')
            text = ''

        return text


if __name__ == '__main__':
    text = SpeechRecognition().recognize()
    print(text)
