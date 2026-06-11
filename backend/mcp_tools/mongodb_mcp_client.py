import os
import asyncio
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.stdio import (
    StdioServerParameters,
    stdio_client,
)

load_dotenv()


class MongoMCPClient:

    def __init__(self):
        self.session = None
        self.transport_ctx = None
        self.session_ctx = None
        self._lock = None  # lazy init inside running event loop

    def _get_lock(self) -> asyncio.Lock:
        """Lazily create the lock inside the running event loop."""
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def connect(self):
        if self.session:
            return

        async with self._get_lock():
            # Double-checked locking: re-check after acquiring
            if self.session:
                return

            print("CONNECT 1")
            server = StdioServerParameters(
                command="npx",
                args=["mongodb-mcp-server"],
            )

            print("CONNECT 2")
            self.transport_ctx = stdio_client(server)
            read_stream, write_stream = await self.transport_ctx.__aenter__()

            print("CONNECT 3")
            self.session_ctx = ClientSession(read_stream, write_stream)
            self.session = await self.session_ctx.__aenter__()

            print("CONNECT 4")
            await self.session.initialize()
            print("CONNECT 5: Authenticating with MongoDB")

            await self.session.call_tool(
                "connect",
                {"connectionString": os.getenv("MONGODB_URI")},
            )
            print("MCP CONNECTED")

    async def call_tool(self, tool_name: str, arguments: dict):
        # Ensure connected before every call (no-op if already connected)
        await self.connect()
        # No lock needed here: MCP stdio sessions handle one request at a time
        # and the connect lock above already serialises the initialisation path.
        result = await self.session.call_tool(tool_name, arguments)
        return result


mongodb_mcp_client = MongoMCPClient()