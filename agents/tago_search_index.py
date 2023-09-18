from langchain.tools import Tool
from langchain.utilities import GoogleSearchAPIWrapper

import configparser, os
config = configparser.ConfigParser()
config.read('./keys.ini')
os.environ['GOOGLE_API_KEY'] = config['GOOGLE']['GOOGLE_API_KEY']
os.environ['GOOGLE_CSE_ID'] = config['GOOGLE']['GOOGLE_CSE_ID']
openai_api_key = config['OPENAI']['OPENAI_API_KEY']
os.environ['OPENAI_API_KEY'] = openai_api_key

#https://python.langchain.com/docs/integrations/tools/google_search
#https://stackoverflow.com/questions/37083058/programmatically-searching-google-in-python-using-custom-search

from langchain.agents import load_tools, ZeroShotAgent, Tool, AgentExecutor, initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_memory import ChatMessageHistory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain import LLMChain, PromptTemplate, SerpAPIWrapper
from langchain.chat_models import ChatOpenAI

from langchain.tools import Tool
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.document_loaders import WebBaseLoader

#load index db
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
db = Chroma(persist_directory="./cache", embedding_function=OpenAIEmbeddings())
from langchain.text_splitter import RecursiveCharacterTextSplitter

search = GoogleSearchAPIWrapper()

def top_results(query):
    return search.results(query, 8)

#web load, then add to database
def load_add(link:str):
    #load the link from web; then add the content of the link to database
    loader = WebBaseLoader(link)
    #split the webpage if too long
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 5000, chunk_overlap = 0)
    docs = loader.load_and_split(text_splitter)
    this_id = str(abs(hash(link)) % (10 ** 8))
    this_list =[this_id + "_" + "{0:0=4d}".format(x) for x in range(len(docs))]
    db.add_documents(docs, ids = this_list)

#Search Google and store the results in the vector index
def search_store(query:str):
    #search google about the query
    res = top_results(query)
    tmp = db.get()['ids']
    this_db_set = set([x.split("_")[0] for x in tmp])
    for r in res:
        #if google results not in the database, save it to the database
        this_id = str(abs(hash(r['link'])) % (10 ** 8))
        if not(this_id in this_db_set):
            load_add(r['link'])
    return('RUN SUCCESS: search completed and results stored in vector db')

from langchain.chains import RetrievalQA
llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0)
qa_chain = RetrievalQA.from_chain_type(llm,retriever=db.as_retriever(), chain_type="map_reduce", return_source_documents=True)

#query the results in the vector db
def query_db(query:str):
    return(qa_chain({"query": query}))
         

from langchain.chains import RetrievalQA
llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0)
qa_chain = RetrievalQA.from_chain_type(llm,retriever=db.as_retriever())

#query the results in the vector db
def query_db(query:str):
    return(qa_chain({"query": query}))
         
tools = load_tools(["python_repl"])
tools += [
    Tool(
        name = "Search and store",
        func=search_store,
        description="search for question in google and store it in vector db"
    ),
    Tool(
        name = "query the question in vector db",
        func=query_db,
        description="query the question in vector db and summarize the answer"
    ),
]


#use .ZERO_SHOT_REACT_DESCRIPTION for single input tools
agent = initialize_agent(
    tools, 
    llm, 
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
    verbose=True
)

            
