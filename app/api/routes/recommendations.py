from fastapi import APIRouter, HTTPException, status
from uuid import uuid4

from app.agents.portfolio_agent import PortfolioAgent
from app.clients.market_data import create_market_data_client
from app.core.errors import AppError
from app.core.execution_log import execution_log_recorder
from app.schemas.recommendations import RecommendationRequest, RecommendationResponse
from app.services.allocation import AllocationService
from app.services.portfolio import PortfolioRecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("", response_model=RecommendationResponse)
async def create_recommendation(request: RecommendationRequest) -> RecommendationResponse:
    service = PortfolioRecommendationService(
        agent=PortfolioAgent(),
        market_data_client=create_market_data_client(),
        allocation_service=AllocationService(),
    )
    try:
        response = await service.recommend(request)
    except AppError as exc:
        error_detail = {
            "error": exc.code,
            "message": exc.message,
        }
        execution_id = execution_log_recorder.record(
            route="POST /api/v1/recommendations",
            request=request.model_dump(),
            status="error",
            error=error_detail,
        )
        error_detail["execution_id"] = execution_id
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail,
        ) from exc

    execution_id = str(uuid4())
    response_with_execution_id = response.model_copy(update={"execution_id": execution_id})
    execution_log_recorder.record(
        route="POST /api/v1/recommendations",
        request=request.model_dump(),
        status="success",
        response=response_with_execution_id.model_dump(),
        execution_id=execution_id,
    )
    return response_with_execution_id
