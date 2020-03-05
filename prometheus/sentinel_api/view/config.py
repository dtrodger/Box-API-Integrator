from __future__ import annotations

import aiohttp.web as aiohttp_web
import aiohttp_cors

import prometheus.file_system.files.config_file as prometheus_config_file


class ConfigurationView(aiohttp_web.View, aiohttp_cors.CorsViewMixin):
    async def get(self) -> aiohttp_web.Response:
        dev_config_file = prometheus_config_file.BCAgentConfigFile("dev_local")
        return aiohttp_web.json_response(
            dev_config_file.cached_disk_self,
            status=200,
            content_type="application/json",
        )
