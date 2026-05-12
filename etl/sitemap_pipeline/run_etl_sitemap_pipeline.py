import os
from langchain_community.embeddings import HuggingFaceEmbeddings

from etl.sitemap_pipeline.extractor import run_extracter
from etl.sitemap_pipeline.cleaner import process_cleaning_raw_files
from etl.sitemap_pipeline.chunker import chunk_files
from etl.sitemap_pipeline.ingestion import ingest_chunks_into_chroma
import logging

#---LOGGER CONFIGURATION -------------

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("run_sitemap_etl_pipeline.log")

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


def run_etl_function():
    logger.info("The ETL PIEPLINE HAS STARTED ")

    try:
        logger.info("The Process of extracting and saving the raw file has started")
        run_extracter()
        logger.info("Extractor method  Process Has Been Completed")

    except Exception as e:
        logger.error(f"Extractor methods failed with Error - > {e}")
        raise

    try:
        logger.info("The Process of cleaning and saving the raw file has started")
        process_cleaning_raw_files()
        logger.info("Cleaning   Process Has Been Completed")

    except Exception as e:
        logger.error(f"Cleaning   Process failed with Error - > {e}")
        raise

    try:
        logger.info("The Process of chunking  has started")
        all_chunks = chunk_files()
        logger.info("The Process of chunking  has Finished")


    except Exception as e:
        logger.error(f"Chunking   Process failed with Error - > {e}")
        raise

    try:
        logger.info("The Process of Ingesting  Chunks To Chroma Has Started")
        ingest_chunks_into_chroma(all_chunks)
        logger.info("The Process of Ingesting  has Finished")

    except Exception as e:
        logger.error(f"Ingesting   Process failed with Error - > {e}")
        raise

    logger.info("\n-----------------------------")
    logger.info("All The Process of etl pipeline has completed successfully")
    logger.info("-------------------------------\n")


if __name__ == "__main__":
    run_etl_function()




    


        
        