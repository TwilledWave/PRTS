#from https://github.com/Plachtaa/VITS-fast-fine-tuning

import argparse
import json
import os
import re
import tempfile
import logging

logging.getLogger('numba').setLevel(logging.WARNING)
import librosa

import numpy as np
import torch
from torch import no_grad, LongTensor
import commons
import utils
import models
from models import SynthesizerTrn
from text import text_to_sequence, _clean_text
from text.symbols import symbols
from mel_processing import spectrogram_torch
import psutil
from datetime import datetime

language_marks = {
    "Japanese": "",
    "日本語": "[JA]",
    "简体中文": "[ZH]",
    "English": "[EN]",
    "Mix": "",
}

limitation = os.getenv("SYSTEM") == "spaces"  # limit text and audio length in huggingface spaces


def create_tts_fn(model, hps, speaker_ids):
    def tts_fn(text, speaker, language, speed, is_symbol):
        if limitation:
            text_len = len(re.sub("\[([A-Z]{2})\]", "", text))
            max_len = 150
            if is_symbol:
                max_len *= 3
            if text_len > max_len:
                return "Error: Text is too long", None
        if language is not None:
            text = language_marks[language] + text + language_marks[language]
        speaker_id = speaker_ids[speaker]
        stn_tst = get_text(text, hps, is_symbol)
        with no_grad():
            x_tst = stn_tst.unsqueeze(0)
            x_tst_lengths = LongTensor([stn_tst.size(0)])
            sid = LongTensor([speaker_id])
            audio = model.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=.667, noise_scale_w=0.8,
                                length_scale=1.0 / speed)[0][0, 0].data.cpu().float().numpy()
        del stn_tst, x_tst, x_tst_lengths, sid
        return "Success", (hps.data.sampling_rate, audio)

    return tts_fn


def create_vc_fn(model, hps, speaker_ids):
    def vc_fn(original_speaker, target_speaker, input_audio):
        if input_audio is None:
            return "You need to upload an audio", None
        sampling_rate, audio = input_audio
        duration = audio.shape[0] / sampling_rate
        if limitation and duration > 30:
            return "Error: Audio is too long", None
        original_speaker_id = speaker_ids[original_speaker]
        target_speaker_id = speaker_ids[target_speaker]

        audio = (audio / np.iinfo(audio.dtype).max).astype(np.float32)
        if len(audio.shape) > 1:
            audio = librosa.to_mono(audio.transpose(1, 0))
        if sampling_rate != hps.data.sampling_rate:
            audio = librosa.resample(audio, orig_sr=sampling_rate, target_sr=hps.data.sampling_rate)
        with no_grad():
            y = torch.FloatTensor(audio)
            y = y.unsqueeze(0)
            spec = spectrogram_torch(y, hps.data.filter_length,
                                     hps.data.sampling_rate, hps.data.hop_length, hps.data.win_length,
                                     center=False)
            spec_lengths = LongTensor([spec.size(-1)])
            sid_src = LongTensor([original_speaker_id])
            sid_tgt = LongTensor([target_speaker_id])
            audio = model.voice_conversion(spec, spec_lengths, sid_src=sid_src, sid_tgt=sid_tgt)[0][
                0, 0].data.cpu().float().numpy()
        del y, spec, spec_lengths, sid_src, sid_tgt
        return "Success", (hps.data.sampling_rate, audio)

    return vc_fn


def get_text(text, hps, is_symbol):
    text_norm = text_to_sequence(text, hps.symbols, [] if is_symbol else hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = LongTensor(text_norm)
    return text_norm


def create_to_symbol_fn(hps):
    def to_symbol_fn(is_symbol_input, input_text, temp_text):
        return (_clean_text(input_text, hps.data.text_cleaners), input_text) if is_symbol_input \
            else (temp_text, temp_text)

    return to_symbol_fn


with open("pretrained_models/info.json", "r", encoding="utf-8") as f:
     models_info = json.load(f)

models_tts = []
models_vc = []

info = models_info['Trilingual']
name = info['title']
lang = info['language']
examples = info['example']
config_path = info['config_path']
model_path = info['model_path']
description = info['description']

hps = utils.get_hparams_from_file(config_path)
#model = ONNXVITS_infer.SynthesizerTrn(
model = SynthesizerTrn(
    len(hps.symbols),
    hps.data.filter_length // 2 + 1,
    hps.train.segment_size // hps.data.hop_length,
    n_speakers=hps.data.n_speakers,
    **hps.model)
utils.load_checkpoint(model_path, model, None)
model.eval()
speaker_ids = hps.speakers
speakers = list(hps.speakers.keys())
models_tts.append((name, description, speakers, lang, examples,
                   hps.symbols, create_tts_fn(model, hps, speaker_ids),
                   create_to_symbol_fn(hps)))
models_vc.append((name, description, speakers, create_vc_fn(model, hps, speaker_ids)))

tts = models_tts[0][6]
char = "雷电将军 Raiden Shogun (Genshin Impact)"
def tts_fn(input_text, lang = ""):
    if lang == 'en':
        return tts(input_text,char,"English",0.6,False)
    elif lang == 'jp':
        return tts(input_text,char,"日本語",1,False)
    elif lang == 'cn':
        char = 
        return tts(input_text,char,"简体中文",0.8,False)
    else:
        return tts(input_text,char,"Mix",0.8,False)

# test case
# tts = models_tts[0][6]
# o3, o4 = tts("good morning command its such a nice day","雷电将军 Raiden Shogun (Genshin Impact)","English",1,False)
# o3, o4 = tts("授業中に出しだら，学校生活終わるですわ。","雷电将军 Raiden Shogun (Genshin Impact)","日本語",1,False)
# o3, o4 = tts("你好，训练员先生，很高兴见到你。","雷电将军 Raiden Shogun (Genshin Impact)","简体中文",1,False)
# from scipy.io.wavfile import write
# write('chat.wav',o4[0],o4[1])

# text = """
# [ZH]真正的骑士决不屈服于暴力，在这把战锤面前忏悔吧。[ZH]
# [JA]真の騎士は決して暴力に屈しない。この裁きの鉄槌の前に、おのが行いを悔いるがいい。[JA]
# [EN]A true knight will not bend to the threat of violence. Now, repent for your sins, in front of my warhammer.[EN]
# """
# o3, o4 = tts_fn(text)
# from scipy.io.wavfile import write
# write('tmp.wav',o4[0],o4[1])
# import ctypes
# from ctypes import *
# from ctypes import wintypes as w
# dll = WinDLL('winmm')
# dll.PlaySoundW.argtypes = w.LPCWSTR,w.HMODULE,w.DWORD
# dll.PlaySoundW.restype = w.BOOL
# SND_FILENAME = 0x20000
# dll.PlaySoundW('tmp.wav',None,SND_FILENAME)
