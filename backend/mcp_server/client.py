import json
import os

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


def url() -> str:
    return os.environ.get("BA_MCP_URL", "http://127.0.0.1:8001/mcp")


async def call_tool(name: str, args: dict) -> dict:
    async with streamablehttp_client(url()) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            res = await s.call_tool(name, args)
            text = res.content[0].text if res.content else "{}"
            return json.loads(text)
