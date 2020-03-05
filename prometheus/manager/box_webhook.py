from __future__ import annotations
import logging
import os
import json

import click

import prometheus.file_system.files.config_file as prometheus_config_file
import prometheus.box_webhook.serializer as box_webhook_serializer


log = logging.getLogger(__name__)


MOCK_FILE_UPLOADED_WEBHOOK_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "webhooks", "file_uploaded.json",
)


@click.command()
@click.option(
    "-e",
    "--env-alias",
    default="dev",
    help="configuration environment alias",
    type=str,
)
def demo_webhook_serializer(env_alias: str) -> None:
    # load config file from data/configuration/[env_alias].yml into memory as a dict
    config_file = prometheus_config_file.PrometheusConfigFile.configure(env_alias)
    config_file.log_prometheus_start("running demo_webhook_serializer")

    with open(MOCK_FILE_UPLOADED_WEBHOOK_PATH, "r") as fh:
        file_upload_webhook_dict = json.load(fh)

    serializer = box_webhook_serializer.BoxWebhookSchema()

    file_upload_webhook_model = serializer.load(file_upload_webhook_dict)

    log.info(f"{type(file_upload_webhook_model.detail.source.path_collection.entries[0])}")
