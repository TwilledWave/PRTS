#https://python.langchain.com/docs/integrations/tools/google_search
#https://stackoverflow.com/questions/37083058/programmatically-searching-google-in-python-using-custom-search

from langchain.agents import ZeroShotAgent, Tool, AgentExecutor, initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_memory import ChatMessageHistory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain import LLMChain, PromptTemplate, SerpAPIWrapper
from langchain.chat_models import ChatOpenAI

from langchain.tools import Tool
from langchain.utilities import GoogleSearchAPIWrapper

import configparser, os
config = configparser.ConfigParser()
config.read('./keys.ini')
os.environ['GOOGLE_API_KEY'] = config['GOOGLE']['GOOGLE_API_KEY']
os.environ['GOOGLE_CSE_ID'] = config['GOOGLE']['GOOGLE_CSE_ID']

search = GoogleSearchAPIWrapper()

tool = Tool(
    name="Google Search",
    description="Search Google for recent results.",
    func=search.run,
)

llm = ChatOpenAI(temperature=0.0, model_name = 'gpt-3.5-turbo')
tools = [tool]
agent = initialize_agent(
    tools,
    llm,
    handle_parsing_errors=True,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)
