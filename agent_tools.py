from langchain.agents import Tool

from agents import *

tools = [
    Tool(
        name = "answer story questions using vector db",
        func=prts_query.run,
        description="answer questions using the source docs"
    ),
    Tool(
        name = "output chapter content to html",
        func=prts_html.run,
        description="output the vector db page content of arknigths chapters to html"
    ),
    Tool(
        name = "fan_fiction",
        func=prts_fiction.run,
        description="write a fan fiction"
    ),
]