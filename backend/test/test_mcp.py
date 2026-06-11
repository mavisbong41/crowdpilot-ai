import asyncio

from mcp_tools.mongodb_mcp_client import mongodb_mcp_client


async def main():

    print("STEP 1")

    await mongodb_mcp_client.connect()

    print("STEP 2")

    tools = await mongodb_mcp_client.session.list_tools()

    print("STEP 3")

    print(tools)


asyncio.run(main())