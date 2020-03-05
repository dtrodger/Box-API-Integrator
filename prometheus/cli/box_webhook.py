from __future__ import annotations
from typing import AnyStr

import click

import prometheus.manager.box_webhook as box_webhook_manager


@click.command()
@click.option(
    "-e",
    "--env-alias",
    default="dev_local",
    help="Application configuration file alias",
    type=str,
)
def demo_webhook_serializer(env_alias: AnyStr) -> None:
    box_webhook_manager.demo_webhook_serializer(env_alias)
