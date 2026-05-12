from langchain_text_splitters import RecursiveCharacterTextSplitter

from pathlib import Path
from hashlib import sha256
import json
import logging
import os

######------------ chunker configurati-------------
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

#-------------- Directory Location --------------
PROCESSED_DIR = "data/processed_sitemap_files"
STATE_FILE = "data/processed_sitemap_files/sitemap_chunk_state.json"

os.makedirs(PROCESSED_DIR, exist_ok=True)

#---logger configuration -------------

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("sitemap_chunker.log")

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

file_handler.setFormatter(formatter)

# ---------- CONSOLE HANDLER ----------
console_handler = logging.StreamHandler()

if not logger.handlers:
     logger.addHandler(file_handler)
     logger.addHandler(console_handler)


#------------------- LOAD/SAVE STATE --------------

def load_state():
    if Path(STATE_FILE).exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_state(state):
     with open(STATE_FILE, "w", encoding="utf-8") as f:
          return json.dump(state, f, indent = 2)
     
#------------------ HASH FUNCTION ----------------

def file_hash(file_path):
     with open(file_path, "r", encoding="utf-8") as f:
          return sha256(f.read().encode("utf-8")).hexdigest()
     
# ------- CHUNKER FUNCTION -----------------------

def chunk_text(text : str)-> list:

     splitter = RecursiveCharacterTextSplitter(
          chunk_size = CHUNK_SIZE,
          chunk_overlap = CHUNK_OVERLAP,
          separators = ["\n\n", "\n", ".", " ", ""]
    
     )

     return splitter.split_text(text)

# ---------- MAIN FUNCTION -------------------------

def chunk_files()->dict:
     
     all_chunks = {}     
     state = load_state()
     
     for file in Path(PROCESSED_DIR).glob("*.txt"):


          filename = file.name
          filepath = os.path.join(PROCESSED_DIR, filename)

          try: 

            h = file_hash(filepath)

            if  state.get(filename, {}).get("hash") == h:       
               logger.info(f"File already Chunked, SKIPPING -> {filename}")
               continue
         
            with open(filepath, "r", encoding="utf-8") as f:        
               text = f.read()
               if not text:
                    logger.info(f"NO TEXT AVAILABLE FOR :-> {filename}")
                    continue
                        
            chunks = chunk_text(text)

            logger.info(f"The {filename} Has Been Chunked Successfully")

            all_chunks[filename] = chunks

            #---- update state --------------

            state[filename] = {
                "hash" : h,
                "num_chunks" : len(chunks)
            }

            logger.info(f"{filename} Total Chunks -> {len(chunks)}")

          except Exception as e:
               logger.error(f"Error processing {filename} -> {e}")

     save_state(state)

     return all_chunks


if __name__ == "__main__":
     chunk_files()


      

          


     


     