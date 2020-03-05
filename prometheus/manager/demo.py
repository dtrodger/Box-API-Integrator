from __future__ import annotations
import logging.config
import pprint

import prometheus.file_system.files.config_file as prometheus_config_file
import prometheus.box_client as prometheus_box_client


# Get logger - https://docs.python.org/3/library/logging.html
log = logging.getLogger(__name__)


def demo(env_alias: str) -> None:
    # Loaded .yaml configuration at data/configuration/[env_alias].yaml into dictionary
    config_file = prometheus_config_file.PrometheusConfigFile.configure(env_alias)
    config_file.log_prometheus_start("running example")

    log.info("configuration")
    pprint.pprint(dict(config_file))

    # Init Box client from configuration
    box_client = prometheus_box_client.PrometheusBoxClient(config_file)
    log.info(f"configured Box client {str(box_client)}")

    config_file.log_prometheus_done()