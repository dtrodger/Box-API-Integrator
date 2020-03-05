from __future__ import annotations
import logging.config
from typing import AnyStr

import click

import prometheus.manager.file_system as demo_file_system_manager


log = logging.getLogger(__name__)


@click.command()
@click.option(
    "-e",
    "--env-alias",
    default="dev_local",
    help="Application configuration file alias",
    type=str,
)
def fs_monitor_demo(env_alias: AnyStr) -> None:
    demo_file_system_manager.fs_monitor_demo(env_alias)
