from models import SynthesizerTrn
import sys, os, io
import re
import argparse
import utils
import commons
import json
import torch
from text import text_to_sequence, _clean_text
from torch import no_grad, LongTensor
from scipy.io.wavfile import write


def get_text(text, hps, is_symbol):
    text_norm = text_to_sequence(text, hps.symbols, [] if is_symbol else hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = LongTensor(text_norm)
    return text_norm

def create_tts_fn(net_g_ms, speaker_id, hps_ms):
    def tts_fn(text, language, noise_scale, noise_scale_w, length_scale, is_symbol):
        text = text.replace('\n', ' ').replace('\r', '').replace(" ", "")
        limitation = False;
        if limitation:
            text_len = len(re.sub("\[([A-Z]{2})\]", "", text))
            max_len = 100
            if is_symbol:
                max_len *= 3
            if text_len > max_len:
                return "Error: Text is too long", None
        if not is_symbol:
            if language == 0:
                text = f"[ZH]{text}[ZH]"
            elif language == 1:
                text = f"[JA]{text}[JA]"
            else:
                text = f"[EN]{text}[EN]"
        stn_tst = get_text(text, hps_ms, is_symbol)
        with no_grad():
            x_tst = stn_tst.unsqueeze(0).to(device)
            x_tst_lengths = LongTensor([stn_tst.size(0)]).to(device)
            sid = LongTensor([speaker_id]).to(device)
            audio = net_g_ms.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=noise_scale, noise_scale_w=noise_scale_w,
                                   length_scale=length_scale)[0][0, 0].data.cpu().float().numpy()

        return "Success", (22050, audio)
    return tts_fn

def create_to_symbol_fn(hps):
    def to_symbol_fn(is_symbol_input, input_text, temp_lang):
        if temp_lang == 0:
            clean_text = f'[ZH]{input_text}[ZH]'
        elif temp_lang == 1:
            clean_text = f'[JA]{input_text}[JA]'
        else:
            clean_text = f'[EN]{input_text}[EN]'
        return _clean_text(clean_text, hps.data.text_cleaners) if is_symbol_input else ''

    return to_symbol_fn

def change_lang(language):
    if language == 0:
        return 0.6, 0.668, 1.2
    elif language == 1:
        return 0.6, 0.668, 1
    else:
        return 0.6, 0.668, 1

import ctypes
from ctypes import *
from ctypes import wintypes as w
dll = WinDLL('winmm')
dll.PlaySoundW.argtypes = w.LPCWSTR,w.HMODULE,w.DWORD
dll.PlaySoundW.restype = w.BOOL
SND_FILENAME = 0x20000
#dll.PlaySoundW('test.wav',None,SND_FILENAME)

with open("pretrained_models/info.json", "r", encoding="utf-8") as f:
     models_info = json.load(f)


hps_ms = utils.get_hparams_from_file(r'pretrained_models/config.json')

#load voice model
info = models_info['cn']
i = 'cn'

net_g_ms = SynthesizerTrn(
            len(hps_ms.symbols),
            hps_ms.data.filter_length // 2 + 1,
            hps_ms.train.segment_size // hps_ms.data.hop_length,
            n_speakers=hps_ms.data.n_speakers if info['type'] == "multi" else 0,
            **hps_ms.model)

utils.load_checkpoint(f'pretrained_models/{i}/{i}.pth', net_g_ms, None)

device = torch.device('cuda') 

_ = net_g_ms.eval().to(device)

sid = info['sid']
input_text = "うふふ……"
lang = 0
ns = 0.6
nsw = 0.668
ls = 1.2
symbol_input = True
limitation = False

tts_fn_eula = create_tts_fn(net_g_ms, sid, hps_ms)
#o1, o2 = tts_fn(input_text, lang,  ns, nsw, ls, symbol_input)
#write('test.wav',o2[0],o2[1])

def tts_fn_cn(input_text):
    lang = 0
    ns = 0.6
    nsw = 0.668
    ls = 1.3
    symbol_input = False
    limitation = False
    return tts_fn_eula(input_text, lang,  ns, nsw, ls, symbol_input)


#load 2nd voice model
info = models_info['jp']
i = 'jp'

net_g_ms = SynthesizerTrn(
            len(hps_ms.symbols),
            hps_ms.data.filter_length // 2 + 1,
            hps_ms.train.segment_size // hps_ms.data.hop_length,
            n_speakers=hps_ms.data.n_speakers if info['type'] == "multi" else 0,
            **hps_ms.model)

utils.load_checkpoint(f'pretrained_models/{i}/{i}.pth', net_g_ms, None)
device = torch.device('cuda') 
_ = net_g_ms.eval().to(device)

sid = info['sid']
tts_fn_ayaka = create_tts_fn(net_g_ms, sid, hps_ms)

def tts_fn_jp(input_text):
    lang = 1
    ns = 0.6
    nsw = 0.668
    ls = 1.0
    symbol_input = False
    limitation = False
    return tts_fn_ayaka(input_text, lang,  ns, nsw, ls, symbol_input)

#o3, o4 = tts_fn_jp("はい,ご主人様")
#write('chat.wav',o4[0],o4[1])

#load 3rd EN voice model
hps_ms2 = utils.get_hparams_from_file(r'pretrained_models/trilingual/trilingual.json')

info = models_info['en']
i = 'en'

net_g_ms2 = SynthesizerTrn(
            len(hps_ms2.symbols),
            hps_ms2.data.filter_length // 2 + 1,
            hps_ms2.train.segment_size // hps_ms2.data.hop_length,
            n_speakers=hps_ms2.data.n_speakers if info['type'] == "multi" else 0,
            **hps_ms2.model)

utils.load_checkpoint(f'pretrained_models/trilingual/trilingual.pth', net_g_ms2, None)
device = torch.device('cuda') 
_ = net_g_ms2.eval().to(device)

sid = info['sid']
tts_fn_raiden = create_tts_fn(net_g_ms2, sid, hps_ms2)

def tts_fn_en(input_text):
    lang = 2
    ns = 0.6
    nsw = 0.668
    ls = 1.0
    symbol_input = False
    limitation = False
    return tts_fn_raiden(input_text, lang,  ns, nsw, ls, symbol_input)

def tts_fn(input_text, lang = 'en'):
    ns = 0.6
    nsw = 0.668
    ls = 1.0
    symbol_input = False
    limitation = False    
    if lang == 'en':
        ls = 1.25
        ns = 0.667
        nsw = 0.8
        return tts_fn_raiden(input_text, 2,  ns, nsw, ls, symbol_input)
    elif lang == 'jp':
        return tts_fn_ayaka(input_text, 1,  ns, nsw, ls, symbol_input)
        #return tts_fn_raiden(input_text, 1,  ns, nsw, ls, symbol_input)
    elif lang == 'cn':
        ls = 1.4
        return tts_fn_eula(input_text, 0,  ns, nsw, ls, symbol_input)
        #return tts_fn_raiden(input_text, 0,  ns, nsw, ls, symbol_input)

#o3, o4 = tts_fn("故事概要： 在这个故事中，罗德岛的行动小队来到了一个名为“眼前的伤”的地方",'cn')
#write('chat.wav',o4[0],o4[1])
        
#EN voice

# from TTS.api import TTS
# #disable logging
# import logging
# logging.disable(logging.CRITICAL)

# text_trap = io.StringIO()
# sys.stdout = text_trap

# tts = TTS("tts_models/en/ljspeech/tacotron2-DDC_ph", gpu = True)

# sys.stdout = sys.__stdout__

# response = "hello master"
# text_trap = io.StringIO()
# sys.stdout = text_trap
# tts.tts_to_file(text=response, file_path="chat.wav")
# sys.stdout = sys.__stdout__