from __future__ import annotations
from typing import AnyStr
import logging

import click

import prometheus.manager.redis_client as redis_client_manager


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
    "--redis-key",
    "-k",
    default="example:key",
    help="Application configuration file alias",
    type=str,
)
def redis_delete(env_alias: AnyStr, redis_key: AnyStr) -> None:
    redis_client_manager.redis_delete(env_alias, redis_key)


@click.command()
@click.option(
    "-e",
    "--env-alias",
    default="dev_local",
    help="Application configuration file alias",
    type=str,
)
@click.option(
    "--redis-key",
    "-k",
    default="example:key",
    help="Application configuration file alias",
    type=str,
)
def redis_get(env_alias: AnyStr, redis_key: AnyStr) -> None:
    redis_client_manager.redis_get(env_alias, redis_key)


@click.command()
@click.option(
    "-e",
    "--env-alias",
    default="dev_local",
    help="Application configuration file alias",
    type=str,
)
@click.option(
    "--redis-key",
    "-k",
    default="example:key",
    help="configuration file alias",
    type=str,
)
def redis_hgetall(env_alias: AnyStr, redis_key: AnyStr) -> None:
    redis_client_manager.redis_hgetall(env_alias, redis_key)


@click.command()
@click.option(
    "-e",
    "--env-alias",
    default="dev_local",
    help="Application configuration file alias",
    type=str,
)
def redis_flush(env_alias: AnyStr) -> None:
    redis_client_manager.redis_flush(env_alias)


@click.command()
@click.option(
    "-e",
    "--env-alias",
    default="dev_local",
    help="Application configuration file alias",
    type=str,
)
@click.option(
    "--redis-key-pattern",
    "-k",
    default="box-folder-path-id:*",
    help="configuration file alias",
    type=str,
)
def redis_scan_keys(env_alias: AnyStr, redis_key_pattern: AnyStr) -> None:
    redis_client_manager.redis_scan_keys(env_alias, redis_key_pattern)


@click.command()
@click.option(
    "-e",
    "--env-alias",
    default="dev_local",
    help="Application configuration file alias",
    type=str,
)
@click.option(
    "--redis-key-pattern",
    "-k",
    default="kkr:box-folder-path-id:*",
    help="configuration file alias",
    type=str,
)
def redis_scan_keys_values(env_alias: AnyStr, redis_key_pattern: AnyStr) -> None:
    redis_client_manager.redis_scan_keys_values(env_alias, redis_key_pattern)


@click.command()
@click.option(
    "-e",
    "--env-alias",
    default="dev_local",
    help="Application configuration file alias",
    type=str,
)
@click.option(
    "--redis-key",
    "-k",
    default="example:key",
    help="Application configuration file alias",
    type=str,
)
@click.option(
    "--redis-value",
    "-v",
    default="example value",
    help="Application configuration file alias",
    type=str,
)
def redis_set(env_alias: AnyStr, redis_key: AnyStr, redis_value: AnyStr) -> None:
    redis_client_manager.redis_set(env_alias, redis_key, redis_value)
