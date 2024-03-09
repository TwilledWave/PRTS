# PRTS

Vector database of Arknights Stories 明日方舟剧情库，可加入任何Langchain AI系统

Ready to use in the language models via LangChain & Chroma

To write fan fictions and answer story questions.

Built by summarizing the story diaglogues on arknights.fandom.com and prts.wiki

Including all stories to the current CN event. [ChromaDB folders](https://github.com/TwilledWave/PRTS/tree/main/db). [HTML story snippets with CG](https://github.com/TwilledWave/PRTS/tree/main/summary_html). 

## Latest update:
03/07/24: Add translation function in AI-voiced audiobook

02/25/24: New function: compile AI-voiced audiobook via [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)

[Change Log](https://github.com/TwilledWave/PRTS/blob/main/ChangeLog.md)

## How to use:

### compile AI-voiced audiobook from any story script in the PRTS link

```
link = "https://prts.wiki/index.php?title=RO3-END-3/NBT&action=edit"
link2video(link, stage = "RO3-END-3", lang = "zh", writeclip = True);
```

compile EN audio from CN script, using translation

```
link2video(link, stage = "RO3-END-3", lang = "zh", writeclip = True, lang_to = "en", translate = True);
```

Sample: Lucent Arrowhead AI Voice

[![Chap13 AI-voice Sample](https://img.youtube.com/vi/JwCrlk85Brw/0.jpg)](https://www.youtube.com/watch?v=JwCrlk85Brw&list=PLs8TZNEg0Ubg9kNm1gEA9PBPJQqyLoC5u&index=3&t=1s&ab_channel=TwilledWave "Lucent Arrowhead AI Voice")

[Use cases in video/prts2video.ipynb](https://github.com/TwilledWave/PRTS/blob/main/video/prts2video.ipynb)

[VA list](https://github.com/TwilledWave/PRTS/blob/main/video/voice.json)

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

