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

# import pyaudio
from gtts import gTTS
from transformers import pipeline

from assistant.utils import playsound
from assistant.utils.colors import bcolors
from assistant.utils.pyaudio_logs import noalsaerr

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
print = lambda *args, **kwargs: None  # Don't print


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
    # Parse args
    args = parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Create recognizer
    r = sr.Recognizer()
    r.energy_threshold = args.energy_threshold
    r.dynamic_energy_threshold = False

    while True:
        try:
            with noalsaerr() as n, sr.Microphone() as source:
                # TODO ad wake up keyword polyxia
                # Speech to text
                logger.info("Listening...")
                audio = r.listen(source)
                text = speech_to_text(audio)

                logger.info(f"{bcolors.RED}Human: {text} {bcolors.ENDC}")

                if text is not None:
                    response = nlu(text)
                    try:
                        language = langdetect.detect(response)
                    except langdetect.lang_detect_exception.LangDetectException:
                        language = "en"
                    logger.info(
                        f"{bcolors.GREEN}Polyxia ({language}): {response} {bcolors.ENDC}"
                    )

                    text_to_speech(response, language)

        except KeyboardInterrupt:
            break


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
