from multiprocessing import Process, Queue
import os
import time
import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import SpeechRecognitionEventArgs
from multiprocessing import Queue

from log.config_log import logger

class SpeechRecognition():

    def __init__(self) -> None:
      super().__init__()

      # Start the process for Speech Recognition
      self.message_queue = Queue()
      self.recognize_proc = Process(target=self.speech_to_text_continuous, kwargs={
        "message_queue": self.message_queue,
        "api_key": os.environ.get('SPEECH_API_KEY'),
        "speech_region": os.environ.get('SPEECH_REGION')}, name="T1")
      self.recognize_proc.start()

      self.latest_message = ""

    def speech_to_text_continuous(self, message_queue: Queue, api_key: str, speech_region: str):
        """
        Converts speech to text non-stop
        Documentation: https://learn.microsoft.com/en-gb/azure/ai-services/speech-service/how-to-recognize-speech?pivots=programming-language-python

        This section will need some changes fo you to solve the challenges
        This logic is called by spawning a sub-process from the main game view.
        The main process and this speech recognition process communicate in a one-way manner using Queues.
        The Speech recognition process can send message to the queue which can be then retrieved by the main process.
        """
        done = False

        def stop_cb(evt):
            logger.info(f'CLOSING on {evt}')
            speech_recognizer.stop_continuous_recognition()
            nonlocal done
            done = True

        def recognized_speech(event: SpeechRecognitionEventArgs):
            logger.info(f"Recognized: {event.result.text}")

            if "hello world" in event.result.text.lower():
                message_queue.put("hello world")

            if "jump" in event.result.text.lower():
                logger.info("jump")
                message_queue.put("jump")

            if "up" in event.result.text.lower():
                logger.info("up")
                message_queue.put("up")

            if "down" in event.result.text.lower():
                logger.info("down")
                message_queue.put("down")

            if "left" in event.result.text.lower():
                logger.info("left")
                message_queue.put("left")

            if "right" in event.result.text.lower():
                logger.info("right")
                message_queue.put("right")
                
            if "stop" in event.result.text.lower():
                logger.info("stop")
                message_queue.put("stop")

            if "start" in event.result.text.lower():
                logger.info("start")
                message_queue.put("start")

        # Init engine
        speech_config = speechsdk.SpeechConfig(subscription=api_key, region=speech_region)
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        # Define Callbacks
        speech_recognizer.recognizing.connect(lambda evt: logger.info(f'RECOGNIZING: {evt.result.text}'))
        speech_recognizer.recognized.connect(recognized_speech)

        speech_recognizer.session_started.connect(lambda evt: logger.info(f'SESSION STARTED: {evt}'))
        speech_recognizer.session_stopped.connect(lambda evt: logger.info(f'SESSION STOPPED {evt}'))
        speech_recognizer.canceled.connect(lambda evt: logger.info(f'CANCELED {evt}'))

        speech_recognizer.session_stopped.connect(stop_cb)
        speech_recognizer.canceled.connect(stop_cb)

        speech_recognizer.start_continuous_recognition()
        
        while not done:
            time.sleep(.1)