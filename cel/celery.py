from celery import Celery

import os
from dotenv import load_dotenv
load_dotenv()

celery_app = Celery(
    "cel",
    broker=f"redis://{os.getenv('REDIS_HOST')}:6379/0",
    backend=f"redis://{os.getenv('REDIS_HOST')}:6379/1",
    include=["cel.tasks"],
)


