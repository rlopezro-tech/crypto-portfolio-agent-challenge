from app.schemas.recommendations import ParsedPortfolioIntent, RecommendationResponse


class AllocationService:
    def build_recommendation(self, intent: ParsedPortfolioIntent) -> RecommendationResponse:
        raise NotImplementedError("Allocation service is not implemented yet.")
