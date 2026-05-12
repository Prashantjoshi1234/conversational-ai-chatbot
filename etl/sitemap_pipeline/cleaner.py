import os
import re
import logging
import html

#-------- DIRECTORY LOCATION ----------------------------------

RAW_DIR = "data/raw_sitemap_files"
PROCESSED_DIR = "data/processed_sitemap_files"


#----------- Logger Configuration -------

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("sitemap_cleaner.log")

# ---------- CONSOLE HANDLER ----------
console_handler = logging.StreamHandler()

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

if not logger.handlers:
     logger.addHandler(file_handler)
     logger.addHandler(console_handler)

# ---------TEXT CLEANER-------------------------


MARKETING_PATTERNS = [
    
    r"drop us a line and keep in touch!?",
    r"speak with the klearcom team today!?",
]

def clean_text(text: str) -> str:
    if not text:
        return ""

    # 1️ Decode HTML entities
    text = html.unescape(text)

    # 2️ Remove unicode junk
    text = text.replace("\u00a0", " ")
    text = text.replace("\u200b", "")

    # 3️ Remove marketing / CTA lines
    for pattern in MARKETING_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.MULTILINE)

    # 4️ Normalize whitespace
    text = re.sub(r"[\r\t]+", " ", text) #carriage return tab cleaning(/r and /t)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ ]{2,}", " ", text)

    # 5️ Final trim
    return text.strip()

def process_cleaning_raw_files():

    total_files = 0

    for filename in os.listdir(RAW_DIR):
        
        if not filename.endswith(".txt"):
            logger.info(f"Skipping non-txt file: {filename}")
            continue

        raw_path = os.path.join(RAW_DIR, filename)
        processed_path = os.path.join(PROCESSED_DIR, filename)

        try:
            with open(raw_path, "r", encoding="utf-8") as f:
                raw_text = f.read()

            cleaned_text = clean_text(raw_text)

            if not cleaned_text:
                logger.info(f"Skipped empty(no text available) file : {filename}")
                continue

            with open(processed_path, "w", encoding="utf-8") as f:
                f.write(cleaned_text)

            logger.info(f" Processed : {filename}")
            
            total_files+=1

        except Exception as e:
            logger.error(f"Error Processing file : {filename} with error {e}")

        

    logger.info("\n Raw : Processed completed\n")
    logger.info(f"Total file processed for cleaning : {total_files}")

if __name__ == "__main__":
    process_cleaning_raw_files()
            
