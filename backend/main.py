from fastapi import FastAPI, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from backend.utils.auth_limiter import limiter
from backend.api.chat_routes import router as chat_router
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from backend.api.auth_routes import router as auth_router
from backend.api.uploadpdf_routes import router as uploadpdf_router
from dotenv import load_dotenv
from backend.Authentication.auth_dependencies import get_current_user_role
import os
from fastapi.security import HTTPBearer


load_dotenv()

security = HTTPBearer()

app = FastAPI(
    title="Conversational RAG API",
    description="Backend for RAG-based chatbot",
    version="1.0.0"
)

#------rate_limiter configuration ----

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)

#---------------------------------------

origins = os.getenv("allow_origins", "")

allow_origins = [o.strip() for o in origins.split(",") if o]

app.add_middleware(
    CORSMiddleware,
    allow_origins= allow_origins,   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")

app.include_router(auth_router, prefix="/api")

app.include_router(uploadpdf_router, prefix="/api")



@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Backend is running 🚀"
    }

@app.get("/test", dependencies=[Depends(security)])
def test(user=Depends(get_current_user_role)):
    return {"role": user}
