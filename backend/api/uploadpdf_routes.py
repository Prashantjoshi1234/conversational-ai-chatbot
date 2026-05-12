from typing import List
import os
import json
import hashlib
from fastapi import File, UploadFile, HTTPException, APIRouter, Depends, Request
import logging
from backend.utils.auth_limiter import limiter
from backend.Authentication.auth_dependencies import get_current_user_role
from hashlib import sha256

#---------- logger configuration ---------

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

file_handler = logging.FileHandler("uploadpdf_routes.log")
file_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)

#--------------------------------------------

router = APIRouter()

# ----------------------------


### Directory location -------------

state_dir = "data/raw_uploaded_pdf_files/uploaded_pdf.json"

####Helper Functions-------------



def sha256_bytes(data : bytes):
    return hashlib.sha256(data).hexdigest()

def load_uploaded_pdf_state():
    if os.path.exists(state_dir):
        with open(state_dir, "r", encoding="utf-8") as f:
            return json.load(f)
        
    return {}


def save_state(file_path):
    with open(state_dir, "w", encoding="utf-8") as f:
        json.dump(file_path, f, indent=2)

def get_unique_filename(file_path):
    base, ext = os.path.splitext(file_path)
    counter = 1
    new_path = file_path
    while os.path.exists(new_path):
        new_path = f"{base}({counter}){ext}"
        counter = counter+1

    return new_path

#-------------------API ENDPOINT------------------

@router.post("/upload_pdf")
@limiter.limit("5/minute")
async def upload_file(request: Request, files: List[UploadFile] = File(...), role: str = Depends(get_current_user_role)):

    if role != "admin":
        raise HTTPException(status_code=403, detail = "NOT AUTHORIZED TO ACCESS")

    upload_dir = "data/ramw_uploaded_pdf_files"
    os.makedirs(upload_dir, exist_ok=True)

    state = load_uploaded_pdf_state()

    results = []

    for file in files:

        temp_filename = f"{file.filename}.tmp"
        temp_path = os.path.join(upload_dir, temp_filename)

        hash_obj = sha256()

        with open(temp_path, "wb") as f:
            while True:
                chunk = await file.read(1024)
                if not chunk:
                    break
                hash_obj.update(chunk)
                f.write(chunk)

        file_hash = hash_obj.hexdigest()

        # duplicate check

        if file_hash in state:
            os.remove(temp_path)

            results.append({
                "filename" : file.filename,
                "status" : "duplicate",
                "message" : "same file already uploaded"
            })
            continue

        #Filename conflict check

        final_path = os.path.join(upload_dir, file.filename)
        final_path = get_unique_filename(final_path)

        #Move temp → final

        os.rename(temp_path, final_path)

        #update state

        state[file_hash] = {
            "original_filename" : file.filename,
            "stored_filename" : os.path.basename(final_path)
        }

        results.append({
            "filename" : file.filename,
            "stored_as" : os.path.basename(final_path),
            "status" : "uploaded"
        })

    save_state(state)

    return results


        



