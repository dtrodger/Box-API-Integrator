from __future__ import annotations
from typing import AnyStr
import logging
import subprocess


import prometheus.file_system.files.config_file as prometheus_config_file


log = logging.getLogger(__name__)


def queue_task_worker(env_alias: AnyStr, queue: AnyStr) -> None:
    config_file = prometheus_config_file.PrometheusConfigFile(env_alias)
    config_file.log_prometheus_start("running queue_task_worker", env_alias=env_alias)
    config_file.set_task_queue_env()

    subprocess.run(
        [
            "celery",
            "worker",
            "-A",
            "prometheus.queues.worker.worker",
            "-Q",
            queue,
            "--pidfile=",
        ]
    )


def queue_task_scheduler(env_alias: AnyStr) -> None:
    config_file = prometheus_config_file.PrometheusConfigFile(env_alias)
    config_file.log_prometheus_start(
        "running queue_task_scheduler", env_alias=env_alias
    )
    config_file.set_task_queue_env()

    subprocess.run(
        ["celery", "beat", "-A", "prometheus.queues.worker.worker", "--pidfile="]
    )


def queue_admin(env_alias: AnyStr) -> None:
    config_file = prometheus_config_file.PrometheusConfigFile(env_alias)
    config_file.log_prometheus_start("running queue_admin", env_alias=env_alias)
    config_file.set_task_queue_env()

    subprocess.run(
        [
            "flower",
            "-A",
            "prometheus.queues.worker.worker",
            "--port=5555",
            f"--broker={config_file['queues']['broker_url']}",
        ]
    )
