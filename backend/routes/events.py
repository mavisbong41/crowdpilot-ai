from fastapi import APIRouter, HTTPException, Query

from models.event import EventCreate, EventResponse, EventUpdate
from services.event_service import EventService

router = APIRouter()
event_service = EventService()


@router.post("", response_model=EventResponse, status_code=201)
async def create_event(payload: EventCreate):
    return await event_service.create(payload)


@router.get("", response_model=list[EventResponse])
async def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    return await event_service.list_all(skip=skip, limit=limit)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str):
    event = await event_service.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(event_id: str, payload: EventUpdate):
    if not payload.model_fields_set:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    existing = await event_service.get_by_id(event_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Event not found")

    merged = existing.model_dump()
    merged.update(payload.model_dump(exclude_unset=True))
    EventCreate.model_validate(merged)

    updated = await event_service.update(event_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated


@router.delete("/{event_id}", status_code=204)
async def delete_event(event_id: str):
    deleted = await event_service.delete(event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Event not found")
