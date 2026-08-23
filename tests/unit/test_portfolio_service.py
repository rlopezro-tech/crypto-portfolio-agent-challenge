from decimal import Decimal

import pytest

from app.agents.portfolio_agent import PortfolioAgent
from app.clients.market_data import DemoMarketDataClient
from app.schemas.recommendations import RecommendationRequest
from app.services.allocation import AllocationService
from app.services.portfolio import PortfolioRecommendationService


@pytest.mark.anyio
async def test_portfolio_service_builds_recommendation_end_to_end_with_demo_data() -> None:
    service = PortfolioRecommendationService(
        agent=PortfolioAgent(use_ai=False),
        market_data_client=DemoMarketDataClient(),
        allocation_service=AllocationService(),
    )

    response = await service.recommend(
        RecommendationRequest(
            message="I want to invest $1000 in low risk cryptocurrencies and prefer BTC."
        )
    )

    assert response.request.budget_usd == Decimal("1000")
    assert response.request.risk_level == "low"
    assert [allocation.ticker for allocation in response.allocations] == ["BTC", "ETH", "PAXG"]
    assert response.total_allocated_usd == Decimal("1000.00")
