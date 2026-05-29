from fastapi import APIRouter, HTTPException, Query

from models.operation_plan import (
    OperationPlanCreate,
    OperationPlanResponse,
    OperationPlanUpdate,
)
from services.plan_service import PlanService

router = APIRouter()
plan_service = PlanService()


@router.post("", response_model=OperationPlanResponse, status_code=201)
async def create_plan(payload: OperationPlanCreate):
    return await plan_service.create(payload)


@router.get("", response_model=list[OperationPlanResponse])
async def list_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    return await plan_service.list_all(skip=skip, limit=limit)


@router.get("/{plan_id}", response_model=OperationPlanResponse)
async def get_plan(plan_id: str):
    plan = await plan_service.get_by_id(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.put("/{plan_id}", response_model=OperationPlanResponse)
async def update_plan(plan_id: str, payload: OperationPlanUpdate):
    if not payload.model_fields_set:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    updated = await plan_service.update(plan_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Plan not found")
    return updated


@router.delete("/{plan_id}", status_code=204)
async def delete_plan(plan_id: str):
    deleted = await plan_service.delete(plan_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Plan not found")
