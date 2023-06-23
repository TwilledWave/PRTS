#!/usr/bin/env python3

from langchain.agents import ZeroShotAgent, Tool, AgentExecutor, initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_memory import ChatMessageHistory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain import LLMChain, PromptTemplate, SerpAPIWrapper
from langchain.chat_models import ChatOpenAI
import sys, os, io, configparser

#read open api key and search key
config = configparser.ConfigParser()
config.read('./keys.ini')
openai_api_key = config['OPENAI']['OPENAI_API_KEY']
os.environ['OPENAI_API_KEY'] = openai_api_key

SERPAPI_API_KEY = config['SERPAPI']['SERPAPI_API_KEY']

# Define which tools the agent can use to answer user queries
search = SerpAPIWrapper(serpapi_api_key=SERPAPI_API_KEY)
tools = [
    Tool(
        name = "Search",
        func=search.run,
        description="useful for when you need to answer questions about current events, e.g. today's info"
    )
]

from agents import tago_TL

import speech_recognition as sr
from voice import *
import threading

global running

import msvcrt as m
import numpy

#use google trans for language detection
from googletrans import Translator
translator = Translator()

#disable logging
import logging
logging.disable(logging.CRITICAL)

message_history = RedisChatMessageHistory(url='redis://localhost:6379/0', ttl=2000, session_id='chat-buffer')
memory = ConversationBufferMemory(memory_key="chat_history", chat_memory=message_history)

template = """你是"大狗”/"Tago"，一只可爱的狗娘 and a chatbot。

作为狗娘，你可以使用人类的语言。你有着漂亮的黑毛。你称呼我为主人。你很喜欢与主人对话。

Tago will use the search tool to answer master's question in details.

{chat_history}
主人: {input}
{agent_scratchpad}
大狗: """

prompt = PromptTemplate(
    template=template,
    input_variables=["input", "chat_history", "agent_scratchpad"]
)

llm_chain = LLMChain(llm=ChatOpenAI(temperature=1, model_name = 'gpt-3.5-turbo'), prompt=prompt)
agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)
agent_chain = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, memory=memory)

def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever



for i in range(50):
    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Press a key to say something ... ')
        pressedKey = m.getch()
        if pressedKey == b'w':
            print('Start keyboard ... ')
            audio_out = input();
        else:
            print('Start recording ... ')
            audio = r.listen(source)
            try:
                audio_out = r.recognize_whisper_api(audio)
                print(f"Whisper API thinks you said {r.recognize_whisper_api(audio)}")
            except sr.RequestError as e:
                print("Could not request results from Whisper API")
    try:
        #response = llm_chain.predict(input=audio_out)
        response = agent_chain.run(input=audio_out)
        print(response)
    except ValueError as e:
        response = str(e)
        response = remove_suffix(remove_prefix(response,"Could not parse LLM output: `"),"`")
        print(response)

    try:
        response_jp = tago_TL.agent_chain.run(response)
        print(response_jp)
    except ValueError as e:
        response_jp = str(e)
        response_jp = remove_suffix(remove_prefix(response_jp,"Could not parse LLM output: `"),"`")
        print(response_jp)        
        
    res = translator.detect(response)

    if res.lang == 'zh-CN':
        o1, o2 = tts_fn_cn(response)
        write('chat.wav',o2[0],o2[1])
    else:
        text_trap = io.StringIO()
        sys.stdout = text_trap
        tts.tts_to_file(text=response, file_path="chat.wav")
        sys.stdout = sys.__stdout__
    
    o3, o4 = tts_fn_jp(response_jp)
    write('chatJP.wav',o4[0],o4[1])
    def play():
        dll.PlaySoundW('chat.wav',None,SND_FILENAME)
        dll.PlaySoundW('chatJP.wav',None,SND_FILENAME)
    thread = threading.Thread(target=play)
    thread.start()

