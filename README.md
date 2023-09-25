# Tago
AI Assistant Tago with LangChain Agents (Personalized Siri / Alexa / Google Home)

Support CN/EN/JP voice input, CN/JP voice output via SO-VITS, EN voice ouput via TTS
(EN voice output needs more work)

It uses LangChain agents to expend functionality. 

Agents can be added to the 'agents' folder. Their definations are in the agents_tools.py. 

The main script calls the agent scripts for specific functions. It supports:
1. Google search.
2. Write / read reminder.
3. Summarize Arknights lore and store it in vector db for furture use.

The web summary func uses vector db to store the Google search results for future use. If a webpage has not been loaded in the vector db, it will be added to the embedded database in the first query. The vector db saves search results for fast query.

The new vector db + web query function is written in the agents/tago_search_index.py

It's easy to add new agents / func to Tago. New agents are added in the agents folder and defined in the agent_tools.py

