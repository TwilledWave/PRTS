from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_memory import ChatMessageHistory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain import OpenAI, LLMChain
from langchain.utilities import GoogleSearchAPIWrapper

from datetime import date
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from pydantic import BaseModel, Field
from typing import Optional, Type
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun

message_history = RedisChatMessageHistory(url='redis://localhost:6379/0', session_id='reminder')
memory = ConversationBufferMemory(memory_key="chat_history", chat_memory=message_history)

class ToolInput(BaseModel):
    question: str = Field()

class DateTool(BaseTool):
    name = "Date"
    description = "useful for when you need to find today's date"
    args_schema: Type[BaseModel] = ToolInput

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        return date.today().strftime("%B %d, %Y")
    
    async def _arun(self, query: str,  run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Calculator does not support async")

tools = [
Tool.from_function(
        func=DateTool(),
        name="DateTool",
        description="useful for when you need to find today's date"
    )
]

prefix = """You are Tago, a maid in charge of recording master's reminder with date. You will have a conversation with your master, summarize master's reminder in itemized list and add date in the front of the recording. You have access to the following tools:"""
suffix = """Begin!"

Question: {input}
{agent_scratchpad}

Return:
<Date>; 1. <item1>; 2. <item2>, ...

You can find out today's date by python's date function. 
You will calculate the reminder date based on today's date. For example, tomorrow is today's date plus one day.

where you replace <Date>,<item1>,<item2>, ... with your actual answer.
Do nothing else but return the answer.

"""

prompt = ZeroShotAgent.create_prompt(
    tools, 
    prefix=prefix, 
    suffix=suffix, 
    input_variables=["input", "agent_scratchpad"]
)

llm_chain = LLMChain(llm=OpenAI(temperature=1), prompt=prompt)
agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)
agent_chain = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, memory=memory)