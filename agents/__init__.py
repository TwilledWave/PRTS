from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_memory import ChatMessageHistory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain import OpenAI, LLMChain
from langchain.utilities import GoogleSearchAPIWrapper

import time
import speech_recognition as sr

import ctypes
from ctypes import *
from ctypes import wintypes as w
dll = WinDLL('winmm')
dll.PlaySoundW.argtypes = w.LPCWSTR,w.HMODULE,w.DWORD
dll.PlaySoundW.restype = w.BOOL
SND_FILENAME = 0x20000

import configparser, os
config = configparser.ConfigParser()
config.read('./keys.ini')
openai_api_key = config['OPENAI']['OPENAI_API_KEY']
os.environ['OPENAI_API_KEY'] = openai_api_key
os.environ['SERPAPI_API_KEY'] = config['SERPAPI']['SERPAPI_API_KEY']
os.environ['GOOGLE_API_KEY'] = config['GOOGLE']['GOOGLE_API_KEY']
os.environ['GOOGLE_CSE_ID'] = config['GOOGLE']['GOOGLE_CSE_ID']
os.environ['PINECONE_API_KEY'] = config['PINECONE']['PINECONE_API_KEY']
os.environ['PINECONE_API_ENV'] = config['PINECONE']['PINECONE_API_ENV']
os.environ['APIFY_API_TOKEN'] = config['APIFY']['APIFY_API_KEY']

from os.path import dirname, basename, isfile, join
import glob
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

