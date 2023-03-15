
import argparse
import tempfile
import time
from typing import Union
from chatbot.chatgpt import ChatBot
from assistant.utils.colors import bcolors
import openai
import sys
import ftfy
import speech_recognition as sr
# import pyaudio
from gtts import gTTS
from assistant.utils import playsound
import langdetect
import numpy as np
from dotenv import load_dotenv
import os
import re

LLM_BOT = ChatBot(
    "You are a helpful voice assistant like Alexa named Polyxia, your answers are precise and concise.")


def speech_to_text(recognizer: sr.Recognizer, audio: sr.AudioData, model_size: str) -> str:
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        default="base",
        help="Model to use",
        choices=["tiny", "base", "small", "medium", "large"]
    )
    parser.add_argument(
        "--energy_threshold",
        default=1000,
        help="Energy level for mic to detect.",
        type=int
    )
    args = parser.parse_args()
    return args


def get_response(chat_bot, text: str) -> str:
    print("Thinking response...")
    start = time.time()
    response = chat_bot.ask(text)
    end = time.time()
    print("Response took {}".format(end - start))
    return ftfy.fix_text(response)


def text_to_speech(text: str, language: str = 'en'):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_file:
        tts = gTTS(text=text, lang=language)
        tts.save(temp_file.name)
        playsound.playsound(temp_file.name)


def calculator(text: str) -> Union[int, float]:
    # Regular expression to match patterns like "calculate four times three" or "calculate ten minus five"

    # Use regular expression to extract the operation and numbers from the text
    match = re.match(r"calculate (\d+) (\w+) (\d+)", text.strip().lower())
    if not match:
        return None

    operation = match[2]
    num1 = int(match[1])
    num2 = int(match[3])

    # Perform the arithmetic operation
    if operation == "divided":
        result = num1 / num2
    elif operation == "minus":
        result = num1 - num2
    elif operation == "plus":
        result = num1 + num2
    elif operation == "times":
        result = num1 * num2
    else:
        return None

    return result


def nlu(text: str) -> str:
    if re.match(r"calculate (\d+) (\w+) (\d+)", text.strip().lower()):
        print("Calling calculator function")
        return str(calculator(text))
    else:
        return get_response(LLM_BOT, text)


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

                # TODO NLU
                if text is not None:
                    response = nlu(text)
                    try:
                        language = langdetect.detect(response)
                    except langdetect.lang_detect_exception.LangDetectException:
                        language = 'en'
                    print(f"{bcolors.GREEN}Polyxia ({language}): {response} {bcolors.ENDC}")

                    # Speak response
                    text_to_speech(response, language)

        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    main()
