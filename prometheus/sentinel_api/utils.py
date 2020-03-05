from __future__ import annotations

import aiohttp.web as aiohttp_web


def success_resp():
    return aiohttp_web.json_response(
        {"success": True}, status=200, content_type="application/json",
    )
