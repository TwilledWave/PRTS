import chromadb
from json2html import *

#output chapter content to html
def run(query:str):

    client = chromadb.PersistentClient(path="./db/arkdb")

    #print ("find db collection:" + client.list_collections())

    db = client.get_collection("langchain")
    data = db.get()
    tmp = []
    for k in range(len(data["ids"])):
        if data["metadatas"][k]["episode"] == query:
            tmp.append(data["metadatas"][k]);
            tmp[-1]["summary"] = data["documents"][k]

    with open('./output.html', 'w', encoding="utf-8") as f:
        f.write(json2html.convert(json = tmp))
    
    return("success: write query to output.html")