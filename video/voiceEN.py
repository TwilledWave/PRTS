#EN voice
import sys, os, io
from TTS.api import TTS
#disable logging
import logging
logging.disable(logging.CRITICAL)

text_trap = io.StringIO()
sys.stdout = text_trap

tts = TTS("tts_models/en/ljspeech/tacotron2-DDC_ph", gpu = True)

sys.stdout = sys.__stdout__

response = "hello master"
text_trap = io.StringIO()
sys.stdout = text_trap
#tts.tts_to_file(text=response, file_path="chat.wav")
sys.stdout = sys.__stdout__