from __future__ import annotations
import logging

import aiohttp.web as aiohttp_web
import aiohttp_cors

import prometheus.sentinel_api.utils as bc_web_utils


log = logging.getLogger(__name__)


class BoxWebHookView(aiohttp_web.View, aiohttp_cors.CorsViewMixin):
    async def post(self) -> aiohttp_web.Response:
        data = await self.request.post()
        log.info(data)
        return bc_web_utils.success_resp()
