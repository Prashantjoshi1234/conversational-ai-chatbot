from etl.pdf_pipeline.cleaner import run_cleaner
from etl.pdf_pipeline.chunker import chunk_uploaded_pdf_to_txt_files
from etl.pdf_pipeline.ingestion import ingestion
import logging

#---logger configuration -------------

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("etl_pdf_pipeline.log")

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

file_handler.setFormatter(formatter)

if not logger.handlers:
     logger.addHandler(file_handler)

#-------------------------------------------------


def run_pdf_etl_pipeline():


    #STEP 1 
    logger.info("Cleaning and saving raw pdf files into txt to processed directpry has been started")
    run_cleaner()
    logger.info("Cleaning and saving raw pdf files into txt to processed directpry has been completed")

    #STEP 2
    logger.info("Chunking of the txt files have been started")
    all_chunks = chunk_uploaded_pdf_to_txt_files()
    logger.info("Chunking of the txt files have been  completed")


    #STEP 3
    logger.info("Ingestion of the all chunks have been started")
    ingestion(all_chunks)
    logger.info("Ingestion of the all chunks have been completed")

    logger.info("\n==============================")
    logger.info(" ETL PDF PIPELINE COMPLETED")
    logger.info("==============================\n")






     
     
        

