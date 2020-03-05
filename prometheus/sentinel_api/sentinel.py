from __future__ import annotations

import aiohttp_cors
import aiohttp.web as aiohttp_web

import prometheus.sentinel_api.view.config as prometheus_config_view
import prometheus.sentinel_api.view.box_web_hook as prometheus_box_web_hook_view
import prometheus.file_system.files.config_file as prometheus_config_file


class SentinelAPI(aiohttp_web.Application):
    def __init__(
        self, config_file: prometheus_config_file.PrometheusConfigFile, *args, **kwargs
    ) -> None:

        super().__init__(*args, **kwargs)

        self.configure_routes(config_file)

    def configure_routes(self, config_file: prometheus_config_file.PrometheusConfigFile):
        allowed_hosts = {
            allowed_host: aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers=allowed_host,
                allow_headers=allowed_host,
            )
            for allowed_host in config_file["sentinel_api"]["allowed_hosts"]
        }

        cors = aiohttp_cors.setup(self, defaults=allowed_hosts)

        cors.add(
            self.router.add_view("/config", prometheus_config_view.ConfigurationView),
            webview=True,
        )
        cors.add(
            self.router.add_view("/box-webhook", prometheus_box_web_hook_view.BoxWebHookView),
            webview=True,
        )
