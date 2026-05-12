from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from pathlib import Path
import os
from etl.sitemap_pipeline.extractor import load_state as extracter_state
from etl.sitemap_pipeline.chunker import chunk_files
import logging
from dotenv import load_dotenv

load_dotenv()

COLLECTION_NAME = os.getenv("collection_name")

#--------------------DIRECTORY LOCATION ------------------

PROCESSED_DIR = "data/processed_sitemap_files"
CHROMADB_DIR = "chroma_db"


#---LOGGER CONFIGURATION -------------

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("sitemap_ingestion.log")

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

file_handler.setFormatter(formatter)

# ---------- CONSOLE HANDLER ----------
console_handler = logging.StreamHandler()

if not logger.handlers:
     logger.addHandler(file_handler)
     logger.addHandler(console_handler)

#-------------Embedding_model----------------#

embedding_model = HuggingFaceEmbeddings(
     model_name = "sentence-transformers/all-MiniLM-L6-v2"
)

#--------------MAIN FNCTION -------------#

def ingest_chunks_into_chroma(chunk_dict : dict):
     
     state = extracter_state()

     file_to_url = {}

     for data in state.values():
          file_to_url[data["file"]] = data["url"]

    #Initialize vectore store
     vectorstore = Chroma(
         collection_name = COLLECTION_NAME,
         embedding_function = embedding_model,
         persist_directory = CHROMADB_DIR
     )

     total_chunks = 0

     for filename, chunks in chunk_dict.items():
          
          try:
               
            base_file = os.path.basename(filename)

            source_url = file_to_url.get(base_file, base_file)

            documents = []

            logger.info(f"START PROCESSING OF {base_file}")

            for idx,chunk in enumerate(chunks):
               
                chunk = chunk.strip()
               
                if not chunk:
                        logger.info(f"NO CHUNK AVAILABLE FOR {base_file}")
                        continue
               
                logger.info(f"Saving metadata → {base_file} | {source_url}")

                documents.append(
                        Document(
                            page_content = chunk,
                            metadata={
                                "source" : base_file,
                                "url" : source_url,
                                "chunk_id" : idx
                            }
                        )
                )

            added = len(documents)

            if documents:
                    
                    vectorstore.add_documents(documents)
                    total_chunks += (added)

                    logger.info(f" {added} chunks ingested → {base_file} and from {source_url}")

          except Exception as e:
               logger.error(f"ERROR PROCESSING {filename} → {e}")
     

     vectorstore.persist()

     logger.info(f" Total chunks ingested: {total_chunks}")

               

       
          

    
     




