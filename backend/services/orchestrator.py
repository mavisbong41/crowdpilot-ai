from agents.coordinator import CoordinatorAgent
from agents.schemas import CoordinatorInput, CoordinatorOutput
from models.operation_plan import OperationPlanCreate
from services.plan_service import PlanService


class OrchestratorService:
    """Runs the multi-agent coordinator and optionally persists the operation plan."""

    def __init__(
        self,
        coordinator: CoordinatorAgent | None = None,
        plan_service: PlanService | None = None,
    ) -> None:
        self.coordinator = coordinator or CoordinatorAgent()
        self.plan_service = plan_service or PlanService()

    def run_pipeline(self, payload: CoordinatorInput) -> CoordinatorOutput:
        return self.coordinator.run(payload)

    async def run_and_save(self, payload: CoordinatorInput):
        result = self.run_pipeline(payload)
        plan = OperationPlanCreate(
            risk_level=result.operation_plan.risk_level,
            recommendations=result.operation_plan.recommendations,
            generated_at=result.operation_plan.generated_at,
        )
        saved = await self.plan_service.create(plan)
        return result, saved
