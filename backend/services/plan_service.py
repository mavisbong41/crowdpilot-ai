from models.operation_plan import (
    OperationPlanCreate,
    OperationPlanResponse,
    OperationPlanUpdate,
)
from services.base import CRUDService


class PlanService(CRUDService[OperationPlanCreate, OperationPlanUpdate, OperationPlanResponse]):
    collection_name = "operation_plans"
    response_model = OperationPlanResponse
