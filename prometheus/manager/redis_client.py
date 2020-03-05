from __future__ import annotations
from typing import AnyStr
import logging
import asyncio

import prometheus.redis_client as bc_redis_client
import prometheus.file_system.files.config_file as prometheus_config_file


log = logging.getLogger(__name__)


def redis_delete(env_alias: AnyStr, redis_key: AnyStr) -> None:
    config_file = prometheus_config_file.PrometheusConfigFile(env_alias)
    config_file.log_prometheus_start(
        "running redis_delete", env_alias=env_alias, redis_key=redis_key
    )
    redis_client = asyncio.run(bc_redis_client.configure_redis_client(config_file))
    log.info(asyncio.run(bc_redis_client.delete(redis_client, redis_key)))


def redis_get(env_alias: AnyStr, redis_key: AnyStr) -> None:
    config_file = prometheus_config_file.PrometheusConfigFile(env_alias)
    config_file.log_prometheus_start(
        "running redis_get", env_alias=env_alias, redis_key=redis_key
    )
    redis_client = asyncio.run(bc_redis_client.configure_redis_client(config_file))
    log.info(asyncio.run(bc_redis_client.get(redis_client, redis_key)))


def redis_hgetall(env_alias: AnyStr, redis_key: AnyStr) -> None:
    config_file = prometheus_config_file.PrometheusConfigFile(env_alias)
    config_file.log_prometheus_start(
        "running redis_hgetall", env_alias=env_alias, redis_key=redis_key
    )
    redis_client = asyncio.run(bc_redis_client.configure_redis_client(config_file))
    log.info(asyncio.run(redis_client.hgetall(redis_key)))


def redis_flush(env_alias: AnyStr) -> None:
    config_file = prometheus_config_file.PrometheusConfigFile(env_alias)
    config_file.log_prometheus_start("running redis_flush", env_alias=env_alias)
    redis_client = asyncio.run(bc_redis_client.configure_redis_client(config_file))
    log.info(asyncio.run(redis_client.flushdb()))


def redis_scan_keys(env_alias: AnyStr, redis_key_pattern: AnyStr) -> None:
    config_file = prometheus_config_file.PrometheusConfigFile(env_alias)
    config_file.log_prometheus_start(
        "running redis_scan_keys",
        env_alias=env_alias,
        redis_key_pattern=redis_key_pattern,
    )
    redis_client = asyncio.run(bc_redis_client.configure_redis_client(config_file))
    matched_redis_keys = asyncio.run(
        bc_redis_client.scan_keys(redis_client, redis_key_pattern)
    )
    if matched_redis_keys:
        print(f"matched {redis_key_pattern} to {matched_redis_keys[1]} redis keys")


def redis_scan_keys_values(env_alias: AnyStr, redis_key_pattern: AnyStr) -> None:
    config_file = prometheus_config_file.PrometheusConfigFile(env_alias)
    config_file.log_prometheus_start(
        "running redis_scan_keys",
        env_alias=env_alias,
        redis_key_pattern=redis_key_pattern,
    )
    redis_client = asyncio.run(bc_redis_client.configure_redis_client(config_file))
    matched_redis_keys = asyncio.run(redis_client.scan(match=redis_key_pattern))
    if matched_redis_keys:
        for redis_key in matched_redis_keys[1]:
            redis_value = asyncio.run(bc_redis_client.get(redis_client, redis_key))
            print(f"matched redis key {redis_key} value {redis_value}")


def redis_set(env_alias: AnyStr, redis_key: AnyStr, redis_value: AnyStr) -> None:
    config_file = prometheus_config_file.PrometheusConfigFile(env_alias)
    config_file.log_prometheus_start(
        "running redis_set",
        env_alias=env_alias,
        redis_key=redis_key,
        redis_value=redis_value,
    )
    redis_client = asyncio.run(bc_redis_client.configure_redis_client(config_file))
    log.info(asyncio.run(bc_redis_client.set(redis_client, redis_key, redis_value)))
