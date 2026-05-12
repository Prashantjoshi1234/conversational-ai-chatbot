from fastapi import File, UploadFile, HTTPException, APIRouter, Depends, Request
from fastapi import APIRouter
from backend.agent.conversation_agent import ConversationAgent
from backend.utils.rate_limiter import TokenBucket
from pydantic import BaseModel
import logging
from typing import List
from backend.Authentication.auth_dependencies import get_current_user_role


#------- logger configuration ----------

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

file_handler = logging.FileHandler("chat_routes.log")
file_handler.setFormatter(formatter)


console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

#---------------------------------------

router = APIRouter()


agent = ConversationAgent()

# ----------------------------
# Request / Response Schemas
# ----------------------------

class ClearSessionRequest(BaseModel):
    session_id: str

class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]


# ----------------------------
# Chat Endpoint
# ----------------------------


# API-level session buckets
API_REQUESTS_PER_SECOND = 5
session_buckets = {}  # session_id -> TokenBucket

logger.info("chat_routes log creation started")

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, role : str = Depends(get_current_user_role)):

    if role != "admin":
        raise HTTPException(status_code=403, detail = "NOT AUTHORIZED TO ACCESS")
    
    session_id = request.session_id
    message = request.message

    logger.info(f"Chat request received | session_id={session_id}")

    # create API-level session bucket if not exists
    if session_id not in session_buckets:
        session_buckets[session_id] = TokenBucket(capacity=API_REQUESTS_PER_SECOND,
                                                  refill_rate=API_REQUESTS_PER_SECOND)

    api_bucket = session_buckets[session_id]

    # API-level rate limiting
    if not api_bucket.allow_request():
        logger.warning(f"API rate limit exceeded | session_id={session_id}")
        return {"answer": "Too many requests. Please slow down.", "sources": []}

    # handle user message
    response = agent.handle_user_message(session_id=session_id, user_message=message)

    logger.info(f"Chat response generated successfully | session_id={session_id}")
    return response




@router.post("/session/clear")
def clear_session_endpoint(request: ClearSessionRequest):
    try:
        agent.memory.clear_session(request.session_id)
        return {"status": "ok", "message": "Session cleared successfully"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    
