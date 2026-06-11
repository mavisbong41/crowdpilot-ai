import os
import asyncio

from dotenv import load_dotenv

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from adk_agents.root_agent import root_agent

from database.connection import (
    connect_db,
    close_db,
)

load_dotenv()

print("API KEY =", os.getenv("GOOGLE_API_KEY"))


async def main():

    await connect_db()

    try:

        session_service = InMemorySessionService()

        session = await session_service.create_session(
            app_name="crowdpilot",
            user_id="test_user",
        )

        print("\n========================")
        print("SESSION:", session.id)
        print("========================\n")

        runner = Runner(
            agent=root_agent,
            app_name="crowdpilot",
            session_service=session_service,
        )

        message = types.Content(
            role="user",
            parts=[
                types.Part(
                    text="""
Attendance: 18000

Venue Capacity: 20000

Generate complete crowd operation mission.
"""
                )
            ],
        )

        print("RUNNING CROWDPILOT ROOT AGENT...\n")

        final_output = None

        async for event in runner.run_async(
            user_id="test_user",
            session_id=session.id,
            new_message=message,
        ):

            print(event)

            if (
                event.content
                and event.content.parts
                and hasattr(event.content.parts[0], "text")
            ):
                final_output = event.content.parts[0].text

        print("\n========================")
        print("FINAL OUTPUT")
        print("========================")

        print(final_output)

    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())