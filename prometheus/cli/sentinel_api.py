from __future__ import annotations
from typing import AnyStr

import click

import prometheus.manager.sentinel_api as sentinel_api_manager


@click.command()
@click.option(
    "-e",
    "--env-alias",
    default="dev_local",
    help="Application configuration file alias",
    type=str,
)
def sentinel_api_server(env_alias: AnyStr):
    sentinel_api_manager.sentinel_api_server(env_alias)
