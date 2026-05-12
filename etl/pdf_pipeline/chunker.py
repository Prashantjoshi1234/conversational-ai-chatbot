from langchain_text_splitters import RecursiveCharacterTextSplitter 
from pathlib import Path
from hashlib import sha256
import json
import logging


CHUNK_size = 500
PROCESSED_PDF_DIR = "data/processed_pdf_file_dir"
CHUNK_overlap = 50
STATE_FILE = 'data/processed_pdf_file_dirs/uploaded_pdf.json'

#---logger configuration -------------

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("uload_pdf_chunker.log")

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

file_handler.setFormatter(formatter)

if not logger.handlers:
     logger.addHandler(file_handler)

#-------------------------------------------------


#HELPER FUNCTIONS

def file_hash(file_path):
     with open(file_path, "r" , encoding="utf-8") as f:
          return sha256(f.read().encode("utf-8")).hexdigest()

#-------------LOAD/SAVE STATE -----------------

def load_state(STATE_FILE):
     if Path(STATE_FILE).exists():
          with open(STATE_FILE, "r", encoding="utf-8") as f:
               return json.load(f)
          
     return {}

def save_state(state :dict):
     with open(STATE_FILE, "w", "utf-8") as f:
          json.dump(state, f, indent = 2)

#-------------------------------------------------
     

def chunk_text(text:str):
        

        splitter = RecursiveCharacterTextSplitter(
        chunk_size = CHUNK_size,
        chunk_overlap = CHUNK_overlap,
        separators = ["\n\n", "\n", ".", " ", ""]
    )

        return splitter.split_text(text)


#--------------MAIN FUNCTION-----------------

  
def  chunk_uploaded_pdf_to_txt_files(PROCESSED_PDF_DIR):

     state = load_state()
     all_chunks = {}

     for filepath in Path(PROCESSED_PDF_DIR).glob("*.txt"):

          h = file_hash(filepath)
          filename = filepath.name
          pdf_file = filename.replace(".txt", ".pdf")

          if filename in state and state[filename]["hash"]==h:
               logger.info(f"This file {filename} has already present in the state file so skiiping it")
               continue

          with open(filepath, "r", encoding="utf-8") as f:
               text = f.read()

          chunks = chunk_text(text)
          all_chunks[filename] = chunks

          ## update state

          state[filename] = {
               "source_pdf" : pdf_file
               "hash" : h,
               "num_chunks" : len(chunks)
          }

          logger.info(f"For {filename} -> {len(chunks)} has been chunked")

     save_state(state)
     return all_chunks

###-------completed ---------------------------




          











   

        

 
          



