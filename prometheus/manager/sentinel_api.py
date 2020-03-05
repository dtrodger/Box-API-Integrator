from __future__ import annotations
from typing import AnyStr

from aiohttp import web

import prometheus.file_system.files.config_file as prometheus_config_file
import prometheus.sentinel_api.sentinel as prometheus_sentinel


def sentinel_api_server(env_alias: AnyStr) -> None:
    config_file = prometheus_config_file.PrometheusConfigFile(env_alias)
    config_file.log_prometheus_start("running run_web_api", env_alias=env_alias)

    sentinel_api = prometheus_sentinel.SentinelAPI(config_file)
    web.run_app(
        sentinel_api,
        host=config_file["sentinel_api"]["host"],
        port=config_file["sentinel_api"]["port"],
    )
