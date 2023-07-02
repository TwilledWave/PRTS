
csv_location = ''

from langchain.agents import create_csv_agent
from langchain.llms import OpenAI

agent = create_csv_agent(OpenAI(temperature=0, model_name = 'gpt-3.5-turbo'), 
                         '/cache/RePORTER_PRJ_C_FY2022.csv', 
                         verbose=True)

agent_chain = AgentExecutor.from_agent_and_tools(agent=agent, verbose=True)
