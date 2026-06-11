import asyncio

from database.connection import (
    connect_db,
    close_db
)

from mcp_tools.incident_tool import (
    get_playbook_by_incident_type
)


async def main():

    await connect_db()

    result = await get_playbook_by_incident_type(
        "Crowd Surge"
    )

    print(result)

    await close_db()


if __name__ == "__main__":
    asyncio.run(main())