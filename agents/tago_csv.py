
csv_location = ''

from langchain.agents import create_csv_agent
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor

#use a high token count model gpt-3.5-turbo-16k for csv data
agent = create_csv_agent(ChatOpenAI(temperature=0, model_name = 'gpt-3.5-turbo-16k'), 
                         '../cache/RePORTER_PRJ_C_FY2022.csv', 
                         verbose=True)
