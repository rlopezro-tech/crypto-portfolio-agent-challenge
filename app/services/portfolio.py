from app.agents.portfolio_agent import PortfolioAgent
from app.clients.market_data import MarketDataClient
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
