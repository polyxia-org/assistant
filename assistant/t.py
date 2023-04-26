from whispercpp import Whisper
import time 
import ffmpeg
import numpy as np

# try:
#     y, _ = (
#         ffmpeg.input("/home/croumegous/workspace/POC/text-2-text/asr/example.wav", threads=0)
#         .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=16000)
#         .run(
#             cmd=["ffmpeg", "-nostdin"], capture_stdout=True, capture_stderr=True
#         )
#     )
# except Exception as e:
#     raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

# arr = np.frombu

w = Whisper.from_pretrained("small")

start = time.time()
# recognized_text = w.transcribe(arr)
recognized_text = w.transcribe_from_file("/home/croumegous/workspace/POC/text-2-text/asr/jfk.wav")
print(recognized_text)
print(f"Time: {time.time() - start} seconds")