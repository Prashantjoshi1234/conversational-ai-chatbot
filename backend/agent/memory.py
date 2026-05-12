import uuid
from backend.utils.rate_limiter import TokenBucket  

class ConversationMemory:

    def __init__(self, max_history: int = 6):
        self.store = {}
        self.max_history = max_history
        self.llm_buckets = {}  

    def get_bucket(self, session_id: str) -> TokenBucket:
        
        if session_id not in self.llm_buckets:
            self.llm_buckets[session_id] = TokenBucket(capacity=1, refill_rate=1)  # 1 LLM call/sec
        return self.llm_buckets[session_id]

    def add_message(self, session_id: str, role: str, message: str):
       
        if session_id not in self.store:
            self.store[session_id] = []
            self.llm_buckets[session_id] = TokenBucket(capacity=1, refill_rate=1)
            print(f" Warning: Session {session_id} not found, creating new session.")

        self.store[session_id].append((role, message))
        self.store[session_id] = self.store[session_id][-self.max_history:]

    def get_history(self, session_id: str) -> str:
        if session_id not in self.store:
            return ""
        recent_messages = self.store[session_id]
        return "\n".join(f"{role.capitalize()} : {msg}" for role, msg in recent_messages)

    def clear_session(self, session_id: str):
        if session_id not in self.store:
            raise KeyError("Session not found")
        del self.store[session_id]
        if session_id in self.llm_buckets:
            del self.llm_buckets[session_id]
