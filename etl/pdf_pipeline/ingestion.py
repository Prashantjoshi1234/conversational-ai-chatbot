from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
import os
import logging
from etl.pdf_pipeline.chunker import load_state as load_chunker_state
from dotenv import load_dotenv

load_dotenv()

COLLECTION_NAME = os.getenv("collection_name")

#------------logger configuration ----------------

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

fromatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

file_handler = logging.FileHandler("upload_pdf_ingestion.log")

file_handler.setFormatter(fromatter)

if not logger.handlers:
    logger.addHandler(file_handler)

#------------------------------------------------------------

embedding_model = HuggingFaceEmbeddings(
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
)

#-----------Directory Location ----------------

CHROMA_DB_DIR = "chroma_db"


def ingestion(chunk_dict :  dict):

    
    state = load_chunker_state() 

    file_to_pdf = {
        txt_file : data["source_pdf"]
        for txt_file, data in state.items()
        if "source_pdf" in data
    }

    # initialize vectore store
    vectorestore = Chroma(
        collection_name = COLLECTION_NAME,
        embedding_function= embedding_model,
        persist_directory = CHROMA_DB_DIR
    )

    total_chunks = 0

    for file_name, chunks in chunk_dict.items():
        base_file = os.path.basename(file_name)
        pdf_file = file_to_pdf.get(base_file, base_file) # we are giving pdf file for metadat as it for upload_pdf_file

        logger.info(f"Ingesting file: {base_file}")

        documents = []

        for idx, chunk in enumerate(chunks):

            chunk = chunk.strip()
            if not chunk:
                logger.info("no chunk avalilable of {filename}")
                continue
            documents.append(
                Document(
                page_content = chunk,
                metadata = {
                    "source_pdf" : pdf_file,
                    "chunk_id" : idx
                }
                )
            )

        if documents:
            vectorestore.add_documents(documents)
            total_chunks += len(documents)

            logger.info(f"✅ {len(documents)} chunks ingested → {base_file} ")

    
    vectorestore.persist()

    logger.info(f" Total chunks ingested: {total_chunks}")



