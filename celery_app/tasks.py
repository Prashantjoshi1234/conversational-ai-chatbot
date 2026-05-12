from celery_app.celery_config import celery_app
from etl.sitemap_pipeline.run_etl_sitemap_pipeline import run_etl_function
import redis
import os
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.Redis.from_url(
    os.getenv("REDIS_URL")
)

LOCK_KEY = "etl_pipeline_lock"
LOCK_TTL = 60 * 60

@celery_app.task(bind=True)
def run_scheduled_etl(self):
    """
    Scheduled Etl task:
    - Scrape
    - save to text
    - clean
    - chunk
    - Embed
    - store in chroma

    """
    lock = redis_client.lock(LOCK_KEY, timeout=LOCK_TTL)

    have_lock = lock.acquire(blocking=False)

    if not have_lock:
        print("ETL already running. skipping")
        return "ETL already running"

    try:
        print("Etl started with lock")
        run_etl_function()
        print("Etl completed")
        return "ETL Sucess"

    finally:
        lock.release()