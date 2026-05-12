from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
import logging
from typing import List
from backend.utils.auth_limiter import limiter

from sqlalchemy.orm import Session
from backend.database.models import User
from backend.database.connection import get_db
from backend.Authentication.authutils import verify_password, create_access_token
import os

#---------- logger configuration ---------

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

file_handler = logging.FileHandler("auth_routes.log")
file_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)

#--------------------------------------------

router = APIRouter()

# ----------------------------
# Request / Response Schemas
# ----------------------------

class AdminLoginRequest(BaseModel):
    username : str
    password : str = Field(min_length= 6)
    role : str

class TokenResponse(BaseModel):
    access_token : str
    token_type : str


# ----------------------------
# Login  Endpoint
# ----------------------------

logger.info("auth_routes log started")

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def AdminLogin(request : Request,  request_data : AdminLoginRequest ,db : Session = Depends(get_db)):

    username = request_data.username
    received_password = request_data.password
    role = request_data.role

    logger.info(f"Login request received | username ={username}")

    admin_search_id = int(os.getenv("ADMIN_SEARCH_ID"))

    admin = db.query(User).filter(User.id == admin_search_id).first()

    authorized_username = admin.username
    authorized_role = admin.role
    authorized_password = admin.password

    logger.info(f' The authorized username {authorized_username} with athorized role {authorized_role} '
                f'and password  has been successfully fetched from the database')
        
    if role != authorized_role:
        logger.warning("User not found")
        raise HTTPException(status_code=401, detail="Invalid username or password or role")
    
    if not verify_password(received_password, authorized_password):
        logger.warning("Wrong password")
        raise HTTPException(status_code=401, detail="Invalid username or password or role")
    
    token_data = {
        "sub" : admin.username,
        "role" : admin.role
    }
    
    access_token = create_access_token(data = token_data)


    return {
        "access_token" : access_token,
        "token_type" : "bearer"
    }





