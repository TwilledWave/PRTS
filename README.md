# PRTS

Vector database of Arknights Stories 明日方舟剧情库，可加入任何Langchain AI系统

Ready to use in the language models via LangChain & Chroma

To write fan fictions and answer story questions.

Built by summarizing the story diaglogues on arknights.fandom.com and prts.wiki

Including all stories to [chapter 13](https://htmlpreview.github.io/?https://github.com/TwilledWave/PRTS/blob/main/summary_html/episode13.html). [ChromaDB folders](https://github.com/TwilledWave/PRTS/tree/main/db). [HTML story snippets with CG](https://github.com/TwilledWave/PRTS/tree/main/summary_html). 

## Latest update:
11/02/23:  Add "Zwillingstürme im Herbst" events into the db [story summary CN](https://htmlpreview.github.io/?https://github.com/TwilledWave/PRTS/blob/main/summary_html/ZT.html) [EN](https://htmlpreview.github.io/?https://github.com/TwilledWave/PRTS/blob/main/summary_html/ZT_EN.html) [JP](https://htmlpreview.github.io/?https://github.com/TwilledWave/PRTS/blob/main/summary_html/ZT_EN.html)

11/01: Add the experimental feature of auto generating video summary of the stories [db2video](https://github.com/TwilledWave/PRTS/blob/main/video/db2video.ipynb)

[Change Log](https://github.com/TwilledWave/PRTS/blob/main/ChangeLog.md)

To do: improve the video summary function by using char pics in the summary

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

