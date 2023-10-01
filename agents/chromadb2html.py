import chromadb

def chromadb2html(query:str):

    client = chromadb.PersistentClient(path="./cache")

    print ("find db collection:" + client.list_collections())

    db = client.get_collection("langchain")
    data = db.get()
    tmp = []
    for k in range(len(data["ids"])):
        if data["metadatas"][k]["category"] == query:
            tmp.append(data["metadatas"][k]);
            tmp[-1]["summary"] = data["documents"][k]

    with open('./cache/db.html', 'w') as f:
        f.write(json2html.convert(json = tmp))
    
    return("success: write db to db.html")