
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor, initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_memory import ChatMessageHistory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain import LLMChain, PromptTemplate, SerpAPIWrapper
from langchain.chat_models import ChatOpenAI

import os
SERPAPI_API_KEY = os.environ.get('SERPAPI_API_KEY')

# Define which tools the agent can use to answer user queries
search = SerpAPIWrapper(serpapi_api_key=SERPAPI_API_KEY)
tools = [
    Tool(
        name = "Search",
        func=search.run,
        description="useful for when you need to answer questions about current events, e.g. today's info"
    )
]

#use local redis server for the search / chat history buffer, buffer reset in ttl 2000
message_history = RedisChatMessageHistory(url='redis://localhost:6379/0', ttl=2000, session_id='chat-buffer')
memory = ConversationBufferMemory(memory_key="chat_history", chat_memory=message_history)

#search answer template
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

#initialized search agent
llm_chain = LLMChain(llm=ChatOpenAI(temperature=1, model_name = 'gpt-3.5-turbo'), prompt=prompt)
agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)
agent_chain = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, memory=memory)

