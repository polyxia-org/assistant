import argparse
import io
import logging
import os
import tempfile
import time
import warnings

import ftfy
import langdetect
import numpy as np
import requests
import soundfile as sf
import speech_recognition as sr
import torch
from dotenv import load_dotenv

from gtts import gTTS
from transformers import pipeline

from assistant.utils import playsound
from assistant.utils.colors import bcolors
from assistant.utils.pyaudio_logs import noalsaerr

from precise_runner import PreciseEngine, PreciseRunner
from os.path import abspath

# Logging setup
warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

trigger_voice = False
speech_recognizer = sr.Recognizer()

def speech_to_text(audio: sr.AudioData) -> str:
    try:
        logger.info("Recognizing...")
        start = time.time()

        # 16 kHz https://github.com/openai/whisper/blob/28769fcfe50755a817ab922a7bc83483159600a9/whisper/audio.py#L98-L99
        wav_bytes = audio.get_wav_data(convert_rate=16000)
        wav_stream = io.BytesIO(wav_bytes)
        audio_array, sampling_rate = sf.read(wav_stream)
        audio_array = audio_array.astype(np.float32)

        recognized_text = generator(audio_array)["text"].strip()
        end = time.time()
        logger.debug("Took {}".format(end - start))

        return recognized_text
    except sr.UnknownValueError:
        logger.error("Speech Recognition could not understand audio")


def text_to_speech(text: str, language: str = "fr"):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_file:
        tts = gTTS(text=text, lang=language)
        tts.save(temp_file.name)
        playsound.playsound(temp_file.name)


def nlu(text: str) -> str:
    try:
        res = requests.post(os.getenv("NLU_ENDPOINT"), json={"input_text": text})
        res.raise_for_status()
        text_output = res.json().get("response")
        return ftfy.fix_text(text_output)
    except requests.exceptions.HTTPError as err:
        logger.error(f"HTTP error occurred: {err}")
        return "Désolé je ne peux pas vous répondre pour le moment"
    except Exception as err:
        logger.error(f"An error occurred: {err}")
        return "Désolé je ne peux pas vous répondre pour le moment"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--energy_threshold",
        default=1000,
        help="Energy level for mic to detect.",
        type=int,
    )
    parser.add_argument(
        "-v", "--verbose", help="increase output verbosity", action="store_true"
    )
    args = parser.parse_args()
    return args

def main():
    logger.info("Polyxia is started")
    logger.info(f"{bcolors.GREEN}Polyxia (fr): Je suis prête, dites Polyxia ! {bcolors.ENDC}")
    text_to_speech("Je vous écoute", "fr")
    try:
        # Parse args
        args = parse_args()
        if args.verbose:
            logger.setLevel(logging.DEBUG)

        def voice_assist():
            """Listen to the user intent when the wakeword is detected
            """
            # Stop listening to the wake word
            runner.stop()
            # Create recognizer
            with noalsaerr(), sr.Microphone() as source:
                playsound.playsound(abspath("assistant/utils/activate.wav"), True)
                logger.info("Listening...")
                speech_recognizer.energy_threshold = args.energy_threshold
                speech_recognizer.dynamic_energy_threshold = False
                audio = speech_recognizer.listen(source)

                text = speech_to_text(audio)
                logger.info(f"{bcolors.RED}Human: {text} {bcolors.ENDC}")

                if text is not None:
                    response = nlu(text)
                    #response = "Ma réponse"
                    try:
                        language = langdetect.detect(response)
                    except langdetect.lang_detect_exception.LangDetectException:
                        language = "en"
                    logger.info(
                        f"{bcolors.GREEN}Polyxia ({language}): {response} {bcolors.ENDC}"
                    )

                    text_to_speech(response, language)
            # Listening to the wake word again
            with noalsaerr(): 
                logger.info(f"{bcolors.GREEN}Polyxia (fr): Souhaitez-vous autre chose ? Dites Polyxia !{bcolors.ENDC}")
                text_to_speech("Souhaitez-vous autre chose ? Dites Polyxia !", "fr")
                runner.start()


        def trigger_wakeword():
            """Activate listening
            """
            global trigger_voice
            trigger_voice = True
            logger.info("Wake word `Polyxia` detected")
        
        with noalsaerr():
            engine = PreciseEngine('packages/precise-engine/precise-engine', 'polyxia.pb')
            runner = PreciseRunner(engine, on_activation=lambda: trigger_wakeword(), sensitivity=0.8, trigger_level=10)
            runner.start()
    
        while True:
            time.sleep(0.1)
            global trigger_voice
            if trigger_voice:
                voice_assist()
                trigger_voice = False 
    
    except KeyboardInterrupt:
        runner.stop()
    
if __name__ == "__main__":
    load_dotenv()
    if os.getenv("NLU_ENDPOINT") is None:
        raise ValueError("NLU_ENDPOINT not found in environment variables")
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    generator = pipeline(
        model="openai/whisper-base",
        device=device,
        generate_kwargs={"language": "<|fr|>", "task": "transcribe"},
    )
    main()
