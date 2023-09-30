# Tago
Langchain agent test platform:

Functional agents can be added to the agents/ folder, defined in the agents_tools.py.

tago-main.py calls the agents.

Update logs:

09/30/23: Webpage summarize and scrap function for web search
![alt text](https://github.com/TwilledWave/Tago/blob/main/example/webscrap_example_093023.png?raw=true)
agents/webscrap.py extracts the list of story links from the webpage.
agents/websummary.py runs two chains to summarize the main content and extract meta data from web page, results are embedded in vector db. 

Output of the run above:
https://github.com/TwilledWave/Tago/blob/main/example/episode08.html

