from __future__ import annotations
from typing import AnyStr

import click

import prometheus.manager.sentinel_ui as sentinel_ui_manager


@click.command()
@click.option(
    "-e",
    "--env-alias",
    default="dev_local",
    help="Application configuration file alias",
    type=str,
)
def sentinel_ui_server(env_alias: AnyStr):
    sentinel_ui_manager.sentinel_ui_server(env_alias)
