

from langchain.chat_models import ChatOpenAI
from langchain.agents import load_tools, initialize_agent

#use a high token count model gpt-3.5-turbo-16k for csv data
llm = ChatOpenAI(temperature=0, model_name = 'gpt-3.5-turbo-16k')
tools = load_tools(["python_repl"])
agent= initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)

#agent.run("how many rows are in the ../cache/RePORTER_PRJ_C_FY2022.csv ?")