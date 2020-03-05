from __future__ import annotations
import logging.config
from typing import AnyStr

# click command line interface package documentation - https://click.palletsprojects.com/en/7.x/
import click

import prometheus.manager.demo as demo_manager


# Get logger - https://docs.python.org/3/library/logging.html
log = logging.getLogger(__name__)


# Define click command by wrapping function in @click.command() decorator
# specify command line argument flags with @click.option decorator
@click.command()
@click.option(
    "-e",
    "--env-alias",
    default="dev_local",
    help="Application configuration file alias",
    type=str,
)
def demo(env_alias: AnyStr) -> None:
    demo_manager.demo(env_alias)
