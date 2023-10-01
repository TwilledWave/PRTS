#this script summarizes the webpage from URL; writes its page content, meta data into a vector db

from langchain.tools import Tool
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.chat_models import ChatOpenAI


import configparser, os
config = configparser.ConfigParser()
config.read('./keys.ini')
os.environ['GOOGLE_API_KEY'] = config['GOOGLE']['GOOGLE_API_KEY']
os.environ['GOOGLE_CSE_ID'] = config['GOOGLE']['GOOGLE_CSE_ID']
openai_api_key = config['OPENAI']['OPENAI_API_KEY']
os.environ['OPENAI_API_KEY'] = openai_api_key

from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

#web loader and split
def web_loader(link:str):
    #input: link of the web page url
    #web loader
    loader = WebBaseLoader(link)
    docs = loader.load()
    #splitter
    #text_splitter = RecursiveCharacterTextSplitter(chunk_size = 7000, chunk_overlap = 500)
    #docs = text_splitter.split_documents(docs)
    return docs


#story summary chain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
#summary the story dialogue from main page content of the URL
def story_summary(docs):
    #input: docs of the web page

    # Define prompt
    prompt_template = """Write a detailed summary of the story. List each section seperately.:
    "{text}"
    Output ONLY the story summary:"""
    prompt = PromptTemplate.from_template(prompt_template)

    # Define LLM chain
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    # Define StuffDocumentsChain
    stuff_chain = StuffDocumentsChain(
        llm_chain=llm_chain, document_variable_name="text"
    )
    
    return stuff_chain.run(docs)


#summary the metadata of the page
def meta_summary(docs):
    
    # Define prompt for the meta data summary
    prompt_template = """
    The input is an html page.
    Extract the following from the html page input
    1. the title, 
    2. a list of category, seperated by comma
    3. list of characters, seperated by comma
    4. the overall fandom / genere that the pages belong to

    "{input}"
    Outputs:"""
    prompt = PromptTemplate.from_template(prompt_template)
    
    #input the docs and prompt 
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k")

    from langchain.chains import create_extraction_chain

    schema = {
        "properties": {
            "title": {"type": "string"},
            "category": {"type": "string"},
            "characters": {"type": "string"},
            "fandom": {"type": "string"},
        },
        "required": ["title","category","characters","fandom"],
    }

    extracted_content = create_extraction_chain(schema=schema, prompt=prompt, llm=llm).run(docs[0].page_content)
    return extracted_content[0]


#summarize a web page then write to vector db
def websummary(link:str):
    #input: link of the web page to summarize

    #load vector db
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import Chroma
    db = Chroma(persist_directory="./cache", embedding_function=OpenAIEmbeddings())
    #get the db existing id set
    tmp = db.get()['ids']
    this_db_set = set([x.split("_")[0] for x in tmp])
    #check whether the hash link is in the db already
    import hashlib
    this_id = str(int(hashlib.sha1(link.encode("utf-8")).hexdigest(), 16) % (10 ** 8))
    if (this_id in this_db_set):
        return(link+" link already in the db, skip");
    
    #load
    docs = web_loader(link)
    #summarize the story
    story = story_summary(docs)
    #summarize the meta data
    meta = meta_summary(docs)
    meta['source'] = link
    
    #write to vector db
    from langchain.docstore.document import Document
    output_doc = Document(page_content=story, metadata=meta);
    db.add_documents([output_doc], ids = [this_id])
    
    return(output_doc)


#main function, summarize a list of web page then write to vector db
def run(link:str):
    #input: a list of link of the web page to summarize
    import re, time
    link_list = re.findall('[\w/.\:\#\-]+',link)
    for l in link_list:
        if "https:" not in l:
            l = "https://"+l;
        print(websummary(l));
        time.sleep(15)
    return("summarize run successful")
        
#link = "https://arknights.fandom.com/wiki/R8-1/Story"
#print(websummary(link))
               
#link = "['arknights.fandom.com//wiki/R8-1/Story', 'arknights.fandom.com//wiki/R8-2/Story']"
#print(run(link))