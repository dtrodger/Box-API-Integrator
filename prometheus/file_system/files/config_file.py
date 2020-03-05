from __future__ import annotations
import logging.config
from typing import AnyStr, Optional
import os
import datetime
import uuid

import attr
import boxsdk

import prometheus.file_system.files.yml_file as prometheus_yml_file
import prometheus.queues.worker as prometheus_queue_worker


log = logging.getLogger(__name__)


@attr.s
class PrometheusConfigFile(prometheus_yml_file.YMLFile):

    @classmethod
    def configure(
        cls,
        env_alias: str = None,
        file_path: str = None,
        load_from_alias: bool = True,
        configure_logging_on_init: bool = True,
    ):
        if load_from_alias:
            file_path = cls.config_file_path_from_alias(env_alias)

        config_file = cls(file_path)

        config_file.cached_disk_self = config_file.disk_self

        if configure_logging_on_init:
            config_file.configure_logging()

        return config_file

    @staticmethod
    def config_file_path_from_alias(env_alias: AnyStr) -> AnyStr:
        return os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "data",
            "configuration",
            f"{env_alias}.yml",
        )

    def configure_logging(self) -> None:
        log_config = self["log"]
        for handler_alias, handler_config in log_config["handlers"].items():
            if "filename" in handler_config.keys():
                log_file_path = os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "..",
                    "..",
                    "data",
                    "log",
                    handler_config["filename"],
                )
                if not os.path.exists(log_file_path):
                    with open(log_file_path, "w"):
                        pass

                handler_config["filename"] = log_file_path

        logging.config.dictConfig(log_config)
        log.debug(f"{self} configured logging")

    def log_prometheus_start(self, message: AnyStr, **kwargs) -> None:

        if kwargs:
            log_message = f"{message} with kwargs {kwargs}"
        else:
            log_message = message

        log.info(
            f"\n\n\n{'-' * 85}\nBox Consulting Prometheus starting in environment {self['environment']}\n{'-' * 85}\n{log_message}\n\n\n"
        )

    @staticmethod
    def log_prometheus_done() -> None:
        log.info(f"\n\n\n{'-' * 85}\nBox Consulting Prometheus done\n{'-' * 85}\n\n\n")

    @property
    def log(self):
        return log

    def set_task_queue_env(self):
        return prometheus_queue_worker.set_task_queue_env_from_config(self)