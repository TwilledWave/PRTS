# PRTS

Vector database of Arknights Stories 明日方舟剧情库，可加入任何Langchain AI系统

Ready to use in the language models via LangChain & Chroma

To write fan fictions and answer story questions.

Built by summarizing the story diaglogues on arknights.fandom.com and prts.wiki

Including all stories to [chapter 13](https://htmlpreview.github.io/?https://github.com/TwilledWave/PRTS/blob/main/summary_html/episode13.html). [ChromaDB folders](https://github.com/TwilledWave/PRTS/tree/main/db). [HTML story snippets with CG](https://github.com/TwilledWave/PRTS/tree/main/summary_html). 

## Latest update:
10/29: Add NPC naming data for translation [translation script](https://github.com/TwilledWave/PRTS/blob/main/db/db2en.ipynb) [web data scrapy script from arknights.fandom](https://github.com/TwilledWave/PRTS/blob/main/db/quotes_spider_npc.py) 

[Change Log](https://github.com/TwilledWave/PRTS/blob/main/ChangeLog.md)

## How to use:

### load the vector db in Langchain
```
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
db = Chroma(persist_directory="./db/arkdb", embedding_function=OpenAIEmbeddings())
```

[Use cases in prts-main.ipynb](https://github.com/TwilledWave/PRTS/blob/main/prts-main.ipynb)

### answer a question about Arknights story
```
agent_chain("why was Maria kidnapped?")
```

![alt text](https://github.com/TwilledWave/PRTS/blob/main/example/maria.jpg?raw=true)

### write a fan fiction
```
agent_chain.run("write a fan fiction of Nearl passionately kissing Vivana after their match")
```

![alt text](https://github.com/TwilledWave/PRTS/blob/main/example/fanfiction.jpg?raw=true)

