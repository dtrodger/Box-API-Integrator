"""
Box Consulting Celery worker
https://docs.celeryproject.org/en/latest/userguide/application.html
"""

from __future__ import annotations

import os
import logging.config
import json

import celery
import celery.signals as celery_signals

# from ibm_watson import NaturalLanguageClassifierV1

import prometheus.file_system.files.config_file as prometheus_config_file
import prometheus.utils as bc_utils
import prometheus.manager.demo as demo_manager


log = logging.getLogger(__name__)


worker = celery.Celery(os.environ.get("QUEUE_APP", "box-consulting-agent"))
worker.config_from_object("prometheus.queues.celeryconfig")


@celery_signals.setup_logging.connect
def _configure_logging(*args, **kwags):
    logging.config.dictConfig(json.loads(os.environ.get("LOG_CONFIG")))


def set_task_queue_env_from_config(
    env_alias: prometheus_config_file.PrometheusConfigFile,
) -> None:
    os.environ["BROKER_URL"] = env_alias["queues"]["broker_url"]
    os.environ["CELERY_RESULT_BACKEND"] = env_alias["queues"][
        "celery_results_backend"
    ]
    os.environ["LOG_CONFIG"] = json.dumps(env_alias["log"])
    os.environ["QUEUE_APP"] = f'box-consulting-agent-{env_alias["environment"]}'
    os.environ["TASK_DEMO_SCHEDULE"] = env_alias["queues"]["task_demo_schedule"]


# task queue router
# https://docs.celeryproject.org/en/latest/userguide/routing.html
worker.conf.task_routes = {
    "prometheus.queues.worker.demo": {"queue": "default"},
    "prometheus.queues.worker.watson_nlc": {"queue": "default"},
}


# task schedule
# https://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html
worker.conf.beat_schedule = {
    "demo": {
        "task": "prometheus.queues.worker.demo",
        "schedule": bc_utils.float_env_var("TASK_DEMO_SCHEDULE"),
    }
}


# task definition
# https://docs.celeryproject.org/en/latest/userguide/tasks.html
@worker.task
def demo():
    demo_manager.demo("dev_local")


# @worker.task
# def watson_nlc(url, classifier_id, api_key, filepath):
#     text = docx2txt.process(filepath)
#     text = text.strip('\n')
#     text = text.replace('\n', '')
#     text = text.strip('\r')
#     text = text.replace('\r', '')
#     text = text.replace('_', '')
#     text = text[:1020]
#     watson_nlu_client = NaturalLanguageClassifierV1(iam_apikey=api_key, url=url)
#     classes = watson_nlu_client.classify("30e98cx619-nlc-729", clean_text).get_result()
#
#     return json.loads(json.dumps(classes, indent=2))
