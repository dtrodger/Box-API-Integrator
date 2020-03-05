from __future__ import annotations
import logging

import aiohttp.web as aiohttp_web
import aiohttp_cors

import prometheus.sentinel_api.utils as web_api_utils


log = logging.getLogger(__name__)


class UserViewLogin(aiohttp_web.View, aiohttp_cors.CorsViewMixin):
    async def post(self) -> aiohttp_web.Response:
        data = await self.request.post()
        log.info(data)

        return web_api_utils.success_resp()


class UserView(aiohttp_web.View, aiohttp_cors.CorsViewMixin):
    async def post(self) -> aiohttp_web.Response:
        data = await self.request.post()
        log.info(data)

        return web_api_utils.success_resp()

    async def put(self) -> aiohttp_web.Response:
        data = await self.request.post()
        log.info(data)

        return web_api_utils.success_resp()

    async def get(self) -> aiohttp_web.Response:
        data = await self.request.post()
        log.info(data)

        return aiohttp_web.json_response(
            {
                "user": {
                    "email": "jake@jake.jake",
                    "token": "jwt.token.here",
                    "username": "jake",
                    "bio": "I work at statefarm",
                    "image": "none"
                }
            },
            status=200,
            content_type="application/json",
        )
