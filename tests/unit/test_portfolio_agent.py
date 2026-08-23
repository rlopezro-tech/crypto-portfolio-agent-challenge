from decimal import Decimal

import pytest

from app.agents.portfolio_agent import PortfolioAgent, _loads_json_content
from app.core.errors import InvalidPortfolioRequestError
from app.schemas.recommendations import RiskLevel


@pytest.mark.anyio
async def test_fallback_parser_extracts_budget_risk_and_preferences() -> None:
    agent = PortfolioAgent(use_ai=False)

    intent = await agent.parse_intent(
        "I want to invest $1,000 in low risk cryptocurrencies and prefer BTC."
    )

    assert intent.budget_usd == Decimal("1000")
    assert intent.risk_level == RiskLevel.low
    assert intent.preferred_tickers == ["BTC"]


@pytest.mark.anyio
async def test_fallback_parser_extracts_excluded_meme_category() -> None:
    agent = PortfolioAgent(use_ai=False)

    intent = await agent.parse_intent("Invest 500 USD in high risk crypto, exclude meme coins.")

    assert intent.budget_usd == Decimal("500")
    assert intent.risk_level == RiskLevel.high
    assert intent.excluded_categories == ["meme"]


@pytest.mark.anyio
async def test_fallback_parser_requires_budget() -> None:
    agent = PortfolioAgent(use_ai=False)

    with pytest.raises(InvalidPortfolioRequestError) as error:
        await agent.parse_intent("I want low risk crypto and prefer BTC.")

    assert error.value.code == "missing_budget"


def test_ai_json_loader_accepts_fenced_json() -> None:
    payload = _loads_json_content(
        """```json
        {"budget_usd": 1000, "risk_level": "low", "preferred_tickers": ["BTC"], "excluded_tickers": [], "excluded_categories": []}
        ```"""
    )

    assert payload["budget_usd"] == 1000
    assert payload["preferred_tickers"] == ["BTC"]


def test_parser_normalizes_ai_category_aliases() -> None:
    from app.schemas.recommendations import ParsedPortfolioIntent

    agent = PortfolioAgent(use_ai=False)
    intent = agent._normalize_intent(
        ParsedPortfolioIntent(
            budget_usd=Decimal("1000"),
            risk_level=RiskLevel.high,
            excluded_categories=["meme coins"],
        )
    )

    assert intent.excluded_categories == ["meme"]
