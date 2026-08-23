from fastapi import APIRouter, HTTPException, status

from app.core.execution_log import execution_log_recorder
from app.schemas.recommendations import RecommendationRequest

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("")
async def create_recommendation(request: RecommendationRequest) -> None:
    error_detail = {
        "error": "not_implemented",
        "message": "Recommendation flow will be implemented in the next development step.",
        "input": request.model_dump(),
    }
    execution_id = execution_log_recorder.record(
        route="POST /api/v1/recommendations",
        request=request.model_dump(),
        status="error",
        error=error_detail,
    )
    error_detail["execution_id"] = execution_id
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=error_detail,
    )
