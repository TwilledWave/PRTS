from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType

from langchain.tools.yahoo_finance_news import YahooFinanceNewsTool
 

llm = ChatOpenAI(temperature=0.0, model_name = 'gpt-3.5-turbo')
tools = [YahooFinanceNewsTool()]
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)
