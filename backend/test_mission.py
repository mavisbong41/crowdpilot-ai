import asyncio

from models.mission import CoordinatorInput
from services.mission_runtime import mission_runtime

async def main():

    payload = CoordinatorInput(
        event_name="World Cup Final 2026",
        venue_capacity=88000,
        expected_attendance=80000,
    )

    mission = await mission_runtime.create(payload)

    print("\nMission finished:")
    print("Status:", mission.status)

    if mission.result:
        print(mission.result)

asyncio.run(main())