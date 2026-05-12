import time
import threading


class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def allow_request(self):


        with self.lock:

            now = time.time()

            elapsed = now-self.last_refill

            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)

            self.last_refill = now

            if self.tokens >= 1:
                self.tokens = self.tokens - 1
                return True
            
            return False



            
            