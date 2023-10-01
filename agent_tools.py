from langchain.agents import Tool

from agents import *

tools = [
    # Tool(
    #     name = "write diary",
    #     func=tago_diary.agent_chain.run,
    #     description="useful for when you write diary."
    # ),
    # Tool(
    #     name = "write reminder",
    #     func=tago_reminder_writer.agent_chain.run,
    #     description="useful for when you write to reminder."
    # ),
    # Tool(
    #     name = "read reminder",
    #     func=tago_reminder_reader.agent_chain.run,
    #     description="useful for when you read a reminder."
    # ),
    Tool(
        name = "Search",
        #func=tago_search_index.agent.run,
        #func=tago_googlesearch.agent.run,
        func=tago_googlesearch.top_results,
        description="find the URL web link through google search"
    ),
    Tool(
        name = "Web Summary",
        func=websummary.run,
        description="summarize webpage by links"
    ),
    Tool(
        name = "Web Scrap",
        func=webscrap.webscrap,
        description="browser one url and return the list of relevant page links"
    ),    
    # Tool(
    #     name = "CSV tool",
    #     func=tago_csv.agent.run,
    #     description="useful for when you need to answer questions in the csv data"
    # ),
    # Tool(
    #     name = "finance news",
    #     func=tago_yfinancenews.agent.run,
    #     description="answer questions about finance news and stock market today"
    # ),
]