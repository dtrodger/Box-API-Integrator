"""
Celery configuration
https://docs.celeryproject.org/en/latest/userguide/configuration.html
"""

import os
import multiprocessing


broker_url = os.environ["BROKER_URL"]
result_backend = os.environ["CELERY_RESULT_BACKEND"]
worker_concurrency = os.environ.get("CELERYD_CONCURRENCY", multiprocessing.cpu_count())
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "Europe/Oslo"
enable_utc = True
