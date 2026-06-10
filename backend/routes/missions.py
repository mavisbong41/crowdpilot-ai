from typing import Literal

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from agents.schemas import CoordinatorInput
from services.mission_runtime import mission_runtime

router = APIRouter()


class ActionDecision(BaseModel):
    decision: Literal["approved", "rejected"]


@router.post("/start", status_code=202)
async def start_mission(payload: CoordinatorInput):
    mission = mission_runtime.create(payload)
    return {"mission_id": mission.mission_id, "status": mission.status}


@router.get("/{mission_id}")
async def get_mission(mission_id: str):
    mission = mission_runtime.get(mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail="Mission not found")
    return {
        "mission_id": mission.mission_id,
        "status": mission.status,
        "events": mission.events,
        "result": mission.result.model_dump(mode="json") if mission.result else None,
        "action_decisions": mission.action_decisions,
    }


@router.post("/{mission_id}/actions/{action_index}/decision")
async def decide_action(
    mission_id: str,
    action_index: int,
    payload: ActionDecision,
):
    if not mission_runtime.decide_action(mission_id, action_index, payload.decision):
        raise HTTPException(status_code=404, detail="Mission or action not found")
    return {
        "mission_id": mission_id,
        "action_index": action_index,
        "decision": payload.decision,
    }


@router.websocket("/ws/{mission_id}")
async def mission_events(websocket: WebSocket, mission_id: str):
    mission = mission_runtime.get(mission_id)
    if mission is None:
        await websocket.close(code=4404)
        return

    await websocket.accept()
    queue = await mission_runtime.subscribe(mission_id)
    if queue is None:
        await websocket.close(code=4404)
        return

    try:
        for event in mission.events:
            await websocket.send_json(event)
        if mission.status in ("completed", "failed"):
            return

        while True:
            event = await queue.get()
            await websocket.send_json(event)
            if event["type"] in ("mission_completed", "agent_failed"):
                return
    except WebSocketDisconnect:
        pass
    finally:
        mission_runtime.unsubscribe(mission_id, queue)
