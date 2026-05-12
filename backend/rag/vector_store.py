
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv()

load_dotenv()

COLLECTION_NAME = os.getenv("collection_name")


import os

# ----------------------------------
# PATH CONFIG
# ----------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
CHROMA_DB_DIR = os.path.join(BASE_DIR, "chroma_db")

# ----------------------------------
# EMBEDDING MODEL (SAME AS INGESTION)
# ----------------------------------
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ----------------------------------
# LOAD VECTOR STORE
# ----------------------------------
def load_vector_store():
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embedding_model
    )
    return vectorstore


# ----------------------------------
# GET RETRIEVER
# ----------------------------------
def get_retriever(k: int = 4):
    vectorstore = load_vector_store()
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k}
    )
    return retriever
