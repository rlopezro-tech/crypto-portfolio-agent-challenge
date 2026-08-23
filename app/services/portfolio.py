from app.agents.portfolio_agent import PortfolioAgent
from app.clients.market_data import MarketDataClient
from app.schemas.recommendations import RecommendationRequest, RecommendationResponse
from app.services.allocation import AllocationService


class PortfolioRecommendationService:
    def __init__(
        self,
        agent: PortfolioAgent,
        market_data_client: MarketDataClient,
        allocation_service: AllocationService,
    ) -> None:
        self.agent = agent
        self.market_data_client = market_data_client
        self.allocation_service = allocation_service

    async def recommend(self, request: RecommendationRequest) -> RecommendationResponse:
        intent = await self.agent.parse_intent(request.message)
        tickers = self.allocation_service.get_required_tickers(intent)
        quotes = await self.market_data_client.get_quotes(tickers)
        return self.allocation_service.build_recommendation(intent, quotes)
