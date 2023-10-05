# Tago
Langchain agent test platform:

Functional agents can be added to the agents/ folder, defined in the agents_tools.py.

tago-main.py calls the agents.

Update logs:

10/05/23: TTS revamp using the trilingual model from https://github.com/Plachtaa/VITS-fast-fine-tuning. Tago can speak EN / JP / CN now.

09/30/23: Webpage summarize and scrap function for web research
![alt text](https://github.com/TwilledWave/Tago/blob/main/example/webscrap_example_093023.png?raw=true)
agents/webscrap.py extracts the list of story links from the webpage.
agents/websummary.py runs two chains to summarize the main content and extract meta data from web page, results are embedded in vector db. 

Output of the run above:
https://htmlpreview.github.io/?https://github.com/TwilledWave/Tago/blob/main/example/episode08.html

