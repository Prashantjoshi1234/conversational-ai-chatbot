from backend.Authentication.authutils import decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, Security
from fastapi import HTTPException, status
import logging

security = HTTPBearer()

#---------- logger configuration ---------

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

file_handler = logging.FileHandler("auth_dependencies.log")
file_handler.setFormatter(formatter)

if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
    logger.addHandler(file_handler)

#--------------------------------------------

def get_current_user(credentials : HTTPAuthorizationCredentials = Security(security)):

    token = credentials.credentials

    logger.info("Before decode access toke call")

    payload = decode_access_token(token)

    logger.info("After decode access toke call")


    if payload is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid token"
        )
    
    username = payload.get("sub")

    return username

def get_current_user_role(credentials : HTTPAuthorizationCredentials = Security(security)):

    if credentials is None:
        logger.info("No credentials received")
        raise HTTPException(status_code=401, detail="No auth header")
    
    logger.info("getting the credentials")

    token = credentials.credentials

    logger.info("we got the credentials")
    
    logger.info("TOKEN: %s", token)

    payload = decode_access_token(token)

    logger.info("PAYLOAD: %s", payload)

    if payload is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid or expired token"
        )
    
    role = payload.get("role")

    if role is None:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Role not found"
        )

    return role 

