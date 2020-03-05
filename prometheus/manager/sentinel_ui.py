from __future__ import annotations
from typing import AnyStr
import logging
import subprocess


import prometheus.file_system.files.config_file as prometheus_config_file


log = logging.getLogger(__name__)


def sentinel_ui_server(env_alias: AnyStr) -> None:
    config_file = prometheus_config_file.PrometheusConfigFile(env_alias)
    config_file.log_prometheus_start("running run_web_ui", env_alias=env_alias)

    subprocess.run(["npm", "start", "--prefix", "prometheus/sentinel_ui"])
