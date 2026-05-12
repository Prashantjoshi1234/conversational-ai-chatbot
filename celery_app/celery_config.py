from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv
import os

load_dotenv()

broker_url = os.getenv("REDIS_BROKER_URL")
result_url = os.getenv("REDIS_RESULT_URL")

celery_app = Celery(
    "conversational_ai_chatbot",
    broker=broker_url,
    backend=result_url,
    include=["celery_app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=False,
)

celery_app.conf.beat_schedule = {
    "run-etl-every-12-hours": {
        "task": "celery_app.tasks.run_scheduled_etl",
        "schedule": crontab(hour="*/12"),
        "options": {
            "expires": 60*60
        }
    }
}

celery_app.conf.timezone = "Asia/Kolkata"
