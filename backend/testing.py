import asyncio
from mcp_tools.mongodb_mcp_client import mongodb_mcp_client

async def main():
    await mongodb_mcp_client.connect()
    tools = await mongodb_mcp_client.session.list_tools()
    print(tools)

    result = await mongodb_mcp_client.call_tool("find", {"database": "crowdpilot", "collection": "events", "filter": {}})
    print(type(result))
    print(result)

asyncio.run(main())