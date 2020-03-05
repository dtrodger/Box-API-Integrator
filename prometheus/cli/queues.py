from __future__ import annotations
from typing import AnyStr
import logging

import click

import prometheus.manager.queues as queues_manager


log = logging.getLogger(__name__)


@click.command()
@click.option(
    "-e",
    "--env-alias",
    default="dev_local",
    help="Application configuration file alias",
    type=str,
)
@click.option(
    "--queue",
    "-q",
    default="default",
    help="Application configuration file alias",
    type=click.Choice(["default"]),
)
def queue_task_worker(env_alias: AnyStr, queue: AnyStr) -> None:
    queues_manager.queue_task_worker(env_alias, queue)


@click.command()
@click.option(
    "--config-alias",
    "-c",
    default="dev_local",
    help="Application configuration file alias",
    type=click.Choice(["dev_local", "dev_docker"]),
)
def queue_task_scheduler(env_alias: AnyStr) -> None:
    queues_manager.queue_task_scheduler(env_alias)


@click.command()
@click.option(
    "--config-alias",
    "-c",
    default="dev_local",
    help="Application configuration file alias",
    type=click.Choice(["dev_local", "dev_docker"]),
)
def queue_admin(env_alias: AnyStr) -> None:
    queues_manager.queue_admin(env_alias)
