from fastapi import APIRouter, HTTPException, status

from app.schemas.recommendations import RecommendationRequest

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("")
async def create_recommendation(request: RecommendationRequest) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "error": "not_implemented",
            "message": "Recommendation flow will be implemented in the next development step.",
            "input": request.model_dump(),
        },
    )
