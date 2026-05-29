from fastapi import APIRouter, HTTPException, Query

from models.incident import IncidentCreate, IncidentResponse, IncidentUpdate
from services.incident_service import IncidentService

router = APIRouter()
incident_service = IncidentService()


@router.post("", response_model=IncidentResponse, status_code=201)
async def create_incident(payload: IncidentCreate):
    return await incident_service.create(payload)


@router.get("", response_model=list[IncidentResponse])
async def list_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    return await incident_service.list_all(skip=skip, limit=limit)


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: str):
    incident = await incident_service.get_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(incident_id: str, payload: IncidentUpdate):
    if not payload.model_fields_set:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    updated = await incident_service.update(incident_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Incident not found")
    return updated


@router.delete("/{incident_id}", status_code=204)
async def delete_incident(incident_id: str):
    deleted = await incident_service.delete(incident_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Incident not found")
