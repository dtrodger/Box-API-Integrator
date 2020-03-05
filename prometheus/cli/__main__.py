"""
Box Consulting cli
"""

from __future__ import annotations

import click

import prometheus.cli.box_webhook as box_webhook_cli
import prometheus.cli.demo as demo_cli
import prometheus.cli.file_system as scanner_proxy_cli
import prometheus.cli.queues as queues_cli
import prometheus.cli.redis_client as redis_client_cli
import prometheus.cli.sentinel_api as sentinel_api_cli
import prometheus.cli.sentinel_ui as sentinel_ui_cli


@click.group()
def cli() -> None:
    pass


def main():
    [
        cli.add_command(command)
        for command in [
            box_webhook_cli.demo_webhook_serializer,
            demo_cli.demo,
            queues_cli.queue_task_scheduler,
            queues_cli.queue_task_worker,
            queues_cli.queue_admin,
            redis_client_cli.redis_delete,
            redis_client_cli.redis_get,
            redis_client_cli.redis_hgetall,
            redis_client_cli.redis_flush,
            redis_client_cli.redis_scan_keys,
            redis_client_cli.redis_scan_keys_values,
            redis_client_cli.redis_set,
            scanner_proxy_cli.fs_monitor_demo,
            sentinel_api_cli.sentinel_api_server,
            sentinel_ui_cli.sentinel_ui_server,
        ]
    ]
    cli()


if __name__ == "__main__":
    main()
