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

#load the webpage and extract all the links
def link_all(link:str):
    #input: link of the web page url
    #output: the docs with all the links
    from langchain.document_transformers import BeautifulSoupTransformer
    from langchain.document_loaders import AsyncChromiumLoader
    from langchain.document_loaders import AsyncHtmlLoader
    #web loader
    loader = AsyncHtmlLoader([link])
    docs = loader.load()
    #extract the link
    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(docs,tags_to_extract=["a"])
    return docs_transformed

#extract the relevant links from one url
def webscrap(link:str):
    #input: link of the web page url
    #output: the list of relevant links from the web page

    suffix = 'Story'
    
    # Define prompt to extract the links    
    from langchain.prompts import PromptTemplate
    prompt_template = """Extract the following links of from html, in the class of category page member.
    Links are in the format of words then numbers. Output the title and link. 

    An example of the links are.
    Input: XX-1 (/wiki/XX-1)
    Output: 
    title: XX-1
    link: /wiki/XX-1

    "{input}"
    Outputs:"""
    prompt = PromptTemplate.from_template(prompt_template)    
    
    docs = link_all(link)
    text = docs[0].page_content

    #define schema to extract the links
    from langchain.chat_models import ChatOpenAI
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k")
    schema = {
        "properties": {
            "title": {"type": "string"},
            "link": {"type": "string"},
        },
        "required": ["title", "link"],
    }

    # Process the first split
    from langchain.chains import create_extraction_chain
    extracted_content = create_extraction_chain(schema=schema, prompt=prompt, llm=llm).run(text)

    from urllib.parse import urlparse
    hostname = urlparse(link).hostname

    #add the main link
    res = []
    for k in range(len(extracted_content)):
        extracted_content[k]['link'] = hostname + '/' + extracted_content[k]['link'] + '/' + suffix
        res.append(extracted_content[k]['link'])
        
    #return extracted_content
    return res

#link = "https://arknights.fandom.com/wiki/Episode_08"
#link = "https://arknights.fandom.com/wiki/Maria_Nearl_(event)"
#print(webscrap(link))