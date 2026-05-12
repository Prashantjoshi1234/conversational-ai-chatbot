from backend.agent.memory import ConversationMemory
from backend.rag.generator import RAGGenerator
import logging
from backend.utils.rate_limiter import TokenBucket
from threading import Semaphore
import random

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

f = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

fh = logging.FileHandler('conversation_agent.log')
fh.setFormatter(f)

if not logger.handlers:
    logger.addHandler(fh)

# Global concurrency gate (only 1 LLM call at a time)
GLOBAL_LLM_SEMAPHORE = Semaphore(1)


class ConversationAgent:
    """
    Conversation agent handling:
    - memory
    - rate limiting
    - concurrency
    - RAG orchestration
    """

    def __init__(self):
        self.memory = ConversationMemory(max_history=6)
        self.generator = RAGGenerator()

    def handle_user_message(self, session_id: str, user_message: str):

        
        if not user_message or not user_message.strip():
            return {
                "answer": (
                    "I am your Klearcom chatbot assistant. "
                    "I didn’t receive a question. "
                    "You can ask me about our services or company details!"
                ),
                "sources": []
            }

        message = user_message.lower().strip()

     
        greetings = [
            "hi", "hii", "hello", "hey",
            "good morning", "good evening",
            "good afternoon", "namaste"
        ]

        if message in greetings:
            return {
                "answer": "Hello! I am your Klearcom chatbot assistant. How can I help you today?",
                "sources": []
            }

  
        #-- Session Rate Limiting --
        
        bucket = self.memory.get_bucket(session_id)

        if not bucket.allow_request():
            return {
                "answer": "Too many requests. Please wait a moment.",
                "sources": []
            }

        
       
        history = self.memory.get_history(session_id)

        logger.info(f"Session: {session_id}")
        logger.info(f"History: {history}")

        #-- CONTEXTUAL QUERY (ONLY FOR RETRIEVAL)

        if history:
            contextual_query = (
                f"Conversation so far:\n{history}\n\n"
                f"User question:\n{user_message}"
            )
        else:
            contextual_query = user_message

        
        #-- GLOBAL CONCURRENCY CONTROL --
        
        acquired = GLOBAL_LLM_SEMAPHORE.acquire(blocking=False)

        busy_messages = [
            "I'm processing another request, try again in a moment 🙂",
            "Almost ready! Please retry in few seconds.",
            "Working on another query — please wait a bit."
        ]

        if not acquired:
            return {
                "answer": random.choice(busy_messages),
                "sources": []
            }

        try:
            
            # contextual_query → retrieval
            # user_message → final LLM question

            response = self.generator.generate_answer(
                query=user_message,
                contextual_query=contextual_query
            )

            if response is None or "answer" not in response:
                response = {
                    "answer": "Sorry, I could not generate a response. Please try again.",
                    "sources": []
                }

        finally:
            GLOBAL_LLM_SEMAPHORE.release()

        
        #-- Save conversation --
       
        self.memory.add_message(session_id, "user", user_message)
        self.memory.add_message(session_id, "assistant", response["answer"])

        return response

        







        


