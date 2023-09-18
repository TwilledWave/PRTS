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

