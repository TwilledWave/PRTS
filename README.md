# PRTS

Vector database of Arknights Stories 明日方舟剧情库，可加入任何Langchain AI系统

Ready to use in the language models via LangChain & Chroma

To write fan fictions and answer story questions.

Built by summarizing the story diaglogues on arknights.fandom.com and prts.wiki

Including all stories to the current CN event. [ChromaDB folders](https://github.com/TwilledWave/PRTS/tree/main/db). [HTML story snippets with CG](https://github.com/TwilledWave/PRTS/tree/main/summary_html). 

## Latest update:
01/10/24:  Add "To The Grinning Valley" [story summary](https://htmlpreview.github.io/?https://github.com/TwilledWave/PRTS/blob/main/summary_html/TG_CN.html) [EN](https://htmlpreview.github.io/?https://github.com/TwilledWave/PRTS/blob/main/summary_html/TG_EN.html) [JP](https://htmlpreview.github.io/?https://github.com/TwilledWave/PRTS/blob/main/summary_html/TG_JP.html)

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

