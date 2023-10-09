from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain

#query using the stuff summarization chain
def run(query:str):
    #input: the query question
    #output: summary based on the query

    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import Chroma
    db = Chroma(persist_directory="./scappy/arkdb", embedding_function=OpenAIEmbeddings())
    res = db.similarity_search(query, k = 6)
    
    # Define prompt
    prompt_template = """based on the text as the background,  """ 
    + query + 
    """ 
    "{text}"
    Output:"""
    prompt = PromptTemplate.from_template(prompt_template)
    
    # Define LLM chain
    llm = ChatOpenAI(temperature=0.8, model_name="gpt-4")
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    
    # Define StuffDocumentsChain
    stuff_chain = StuffDocumentsChain(
        llm_chain=llm_chain, document_variable_name="text"
    )
    return(stuff_chain.run(res))