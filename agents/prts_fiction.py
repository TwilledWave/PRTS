

#write fan fictions based on the instruction and db as background
def run(instruction:str):
    #input: the instruction for fan fiction
    #output: fiction based on the instruction
    from langchain.chains.llm import LLMChain
    from langchain.prompts import PromptTemplate
    from langchain.chains.combine_documents.stuff import StuffDocumentsChain
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import Chroma
    from langchain.chat_models import ChatOpenAI

    db = Chroma(persist_directory="./db/arkdb", embedding_function=OpenAIEmbeddings())
    res = db.similarity_search(instruction, k = 6)
    
    # Define prompt
    prompt_template = "based on the text as the background, " + instruction + """ 
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

