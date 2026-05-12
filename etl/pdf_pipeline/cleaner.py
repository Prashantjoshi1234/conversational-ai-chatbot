import os
import pdfplumber
import logging
import re
from pathlib import Path

#----logger_configuration-----

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

file_handler = logging.FileHandler("upload_pdf_cleaner.log")
file_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)

#-----------------DIRECTORY LOCATION---------------------------

raw_pdf_files_dir = "data/raw_uploaded_pdf_files"

processed_pdf_files_dir = "data/processed_pdf_files_dir"

#-------- Helper Functions -----------------------------


def remove_page_headers_and_footers(text):

    if not text:
        return ""
    
    text = re.sub(r"Page\s+\d+(\s+of\s+\d+)?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\d+\s*/\s*\d+", "",text)

    text =re.sub(r"\s+", " ", text).strip()

    return text

def remove_weird_characters(text):
    return re.sub(r"[^\x00-\x7F]+", " ", text)

def final_clean_pdf_text(text):
    text = remove_page_headers_and_footers(text)
    text = remove_weird_characters(text)

    return text

#------------------------------------------------

def extract_pdf_text(raw_pdf_files_dir):

    extracted_texts = {}

    for filepath in Path(raw_pdf_files_dir).glob("*.pdf"):
        filename = filepath.stem

        try:
            logger.info(f"Extracting text from : -> {filename}")

            with pdfplumber.open(filepath) as pdf:


                text = "\n".join(
                    page.extract_text() or ""
                    for page in pdf.pages
                )

            if not text.strip():
                logger.warning(f"No text availble for this {filename}")
                continue

            extracted_texts[filename] = text

            
        
        except Exception as e:

            logger.error(f"Error Extracting text from  {filename} : {e}")

    return extracted_texts

def clean_text(extracted_texts : dict):

    raw_texts = extracted_texts

    logger.info("starting of cleaning the text of raw pdf files")

    cleaned_texts = {}

    for filename, text in raw_texts.items():

        text = final_clean_pdf_text(text)

        if not text.strip():
            logger.warning(f"There is no text available for {filename}")
            continue

        cleaned_texts[filename] = text

    logger.info("Completed cleaning of all PDF files")

    return cleaned_texts


def save_cleaned_text(cleaned_texts : dict, processed_pdf_dir):

    logger.info("Starting saving cleaned text files")

    processed_pdf_dir = "data/processed_pdf_files_dir"

    logger.info(f"Processed directory ready: {processed_pdf_dir}")

    os.makedirs(processed_pdf_dir, exist_ok=True)

    for filename, text in cleaned_texts.items():

        filepath = os.path.join(processed_pdf_dir, f"{filename}.txt")

        try:
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text)
            
            logger.info(f"Saved cleaned file: {filename}.txt")

        except Exception as e:
            logger.error(f"Error saving file {filename}: {str(e)}")

    logger.info("Completed saving all cleaned files")

#----MAIN METHOD TO RUN CLEANER -----------------

def run_cleaner():

    logger.info("The run cleaner function has been started for processing all raw pdf files")


    #STEP1 --> EXtracting TEXT From raw pdf files
    extracted_texts = extract_pdf_text()
    logger.info("Text extraction completed")

    #STEP 2--> cleaning the raw text of pdf
    cleaned_texts = clean_text(extracted_texts)
    logger.info("Text cleaning completed")

    #STEP 3--> Saving all the pdf files as txt after cleaning in the processed pdf directory
    save_cleaned_text(cleaned_texts, processed_pdf_files_dir)
    logger.info("Cleaned files saved successfully")