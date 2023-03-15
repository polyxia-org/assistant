import argparse
import os
import tempfile
import time

import ftfy
import langdetect
import numpy as np
import requests
import speech_recognition as sr
from dotenv import load_dotenv

# import pyaudio
from gtts import gTTS

from assistant.utils import playsound
from assistant.utils.colors import bcolors


def speech_to_text(
    recognizer: sr.Recognizer, audio: sr.AudioData, model_size: str
) -> str:
    try:
        print("Recognizing...")
        start = time.time()
        recognized_text = recognizer.recognize_whisper(audio, model=model_size)
        end = time.time()
        print(f"Recognized: {recognized_text}")
        print("Took {}".format(end - start))
        return recognized_text
    except sr.UnknownValueError:
        print("Speech Recognition could not understand audio")


def text_to_speech(text: str, language: str = "en"):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_file:
        tts = gTTS(text=text, lang=language)
        tts.save(temp_file.name)
        playsound.playsound(temp_file.name)


def nlu(text: str) -> str:
    res = requests.post(os.getenv("NLU_ENDPOINT"), json={"input_text": text})
    text_output = res.json().get("response")
    return ftfy.fix_text(text_output)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        default="base",
        help="Model to use",
        choices=["tiny", "tiny.en", "base", "base.en", "small", "medium", "large"],
    )
    parser.add_argument(
        "--energy_threshold",
        default=1000,
        help="Energy level for mic to detect.",
        type=int,
    )
    args = parser.parse_args()
    return args


def main():
    # Parse args
    args = parse_args()

    # Create recognizer
    r = sr.Recognizer()
    r.energy_threshold = args.energy_threshold
    r.dynamic_energy_threshold = False

    # Create microphone
    microphone = sr.Microphone()
    with microphone as source:
        r.adjust_for_ambient_noise(source)

    while True:
        try:
            with microphone as source:
                # TODO ad wake up keyword polyxia
                # Speech to text
                print("Listening...")
                audio = r.listen(source)
                text = speech_to_text(r, audio, args.model)

                print(f"{bcolors.RED}Human: {text} {bcolors.ENDC}")

                if text is not None:
                    response = nlu(text)
                    try:
                        language = langdetect.detect(response)
                    except langdetect.lang_detect_exception.LangDetectException:
                        language = "en"
                    print(
                        f"{bcolors.GREEN}Polyxia ({language}): {response} {bcolors.ENDC}"
                    )

                    text_to_speech(response, language)

        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    load_dotenv()
    if os.getenv("NLU_ENDPOINT") is None:
        raise ValueError("NLU_ENDPOINT not found in environment variables")
    main()
