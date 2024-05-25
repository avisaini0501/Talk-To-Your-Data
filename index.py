from langchain_openai import ChatOpenAI 
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import Milvus
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.embeddings.sentence_transformer import (SentenceTransformerEmbeddings)
from sentence_transformers import SentenceTransformer
from langchain.chains import LLMChain 
import os

os.environ["OPENAI_API_KEY"] = "Your_openai_api_key"


llm = ChatOpenAI(model="model_name", temperature=0.3)

# create the open-source embedding function
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

model = SentenceTransformer("all-MiniLM-L6-v2")

# Memory to store conversation
memory = ConversationBufferMemory(memory_key="history", input_key="question", return_messages=True)

# connect to vector store
vector_db = Milvus(
    embeddings,
    connection_args={"host": "localhost", "port": "19530"},
    collection_name="_CloudburnerKB",
)

# Getting the retriever  
retriever = vector_db.as_retriever()

inScope = 'Prompts/inScope_prompt'

# Reading inscope prompt
with open(inScope+'.txt', encoding="utf-8") as file:
    file_contents = file.read()
    intemplate = file_contents


# -----------------------------------------------------------------------------------------------------------------------------------------------

def get_response(ques:str):
    
    prompt = PromptTemplate(
       input_variables=["history", "context", "question"],
       template=intemplate,
    )

       
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type='stuff',
        retriever=retriever,
        verbose=True,
        chain_type_kwargs={
            "verbose": True,
            "prompt": prompt,
            "memory": memory
        }
    )

    res = qa.invoke({"query": ques})

    return res["result"]


# -----------------------------------------------------------------------------------------------------------------------------#

            









        
    