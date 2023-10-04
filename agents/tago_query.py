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

# Create retriever
from langchain.llms import OpenAI
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo

# Define our metadata
metadata_field_info = [
    AttributeInfo(
        name="category",
        description="category of the event that the text comes from",
        type="string or list[string]",
    ),
]
document_content_description = "story"

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
db = Chroma(persist_directory="./cache", embedding_function=OpenAIEmbeddings())

# Define self query retriver
llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0.4)
retriever = SelfQueryRetriever.from_llm(llm = llm, vectorstore = db, document_contents = document_content_description, metadata_field_info = metadata_field_info)