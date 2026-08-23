from decimal import Decimal

import pytest

from app.clients.market_data import MarketQuote
from app.core.errors import InvalidPortfolioRequestError, MarketDataError
from app.schemas.recommendations import ParsedPortfolioIntent, RiskLevel
from app.services.allocation import DISCLAIMER, AllocationService


def quote(ticker: str, price: str) -> MarketQuote:
    return MarketQuote(ticker=ticker, price_usd=Decimal(price), source="test")


def test_low_risk_allocation_totals_budget_and_calculates_quantities() -> None:
    service = AllocationService()
    intent = ParsedPortfolioIntent(
        budget_usd=Decimal("1000"),
        risk_level=RiskLevel.low,
    )
    quotes = {
        "BTC": quote("BTC", "80000"),
        "ETH": quote("ETH", "2000"),
        "PAXG": quote("PAXG", "3400"),
    }

    response = service.build_recommendation(intent, quotes)

    assert [item.ticker for item in response.allocations] == ["BTC", "ETH", "PAXG"]
    assert response.total_allocated_usd == Decimal("1000.00")
    assert sum(item.amount_usd for item in response.allocations) == Decimal("1000.00")
    assert response.allocations[0].amount_usd == Decimal("450.00")
    assert response.allocations[0].quantity == Decimal("0.00562500")
    assert response.disclaimer == DISCLAIMER


def test_preferred_ticker_is_prioritized_when_compatible_with_risk() -> None:
    service = AllocationService()
    intent = ParsedPortfolioIntent(
        budget_usd=Decimal("1000"),
        risk_level=RiskLevel.medium,
        preferred_tickers=["SOL"],
    )
    quotes = {
        "BTC": quote("BTC", "80000"),
        "ETH": quote("ETH", "2000"),
        "SOL": quote("SOL", "150"),
        "LINK": quote("LINK", "20"),
    }

    response = service.build_recommendation(intent, quotes)

    assert response.allocations[0].ticker == "SOL"
    assert len(response.allocations) == 4
    assert response.total_allocated_usd == Decimal("1000.00")


def test_excluded_meme_category_is_not_selected_for_high_risk() -> None:
    service = AllocationService()
    intent = ParsedPortfolioIntent(
        budget_usd=Decimal("500"),
        risk_level=RiskLevel.high,
        excluded_categories=["meme"],
    )
    quotes = {
        "SOL": quote("SOL", "150"),
        "AVAX": quote("AVAX", "40"),
        "ARB": quote("ARB", "2"),
    }

    response = service.build_recommendation(intent, quotes)

    assert [item.ticker for item in response.allocations] == ["SOL", "AVAX", "ARB"]
    assert response.total_allocated_usd == Decimal("500.00")
    assert all(item.ticker not in {"DOGE", "PEPE"} for item in response.allocations)


def test_raises_when_constraints_leave_too_few_supported_coins() -> None:
    service = AllocationService()
    intent = ParsedPortfolioIntent(
        budget_usd=Decimal("1000"),
        risk_level=RiskLevel.low,
        excluded_tickers=["BTC", "ETH"],
    )

    with pytest.raises(InvalidPortfolioRequestError) as error:
        service.build_recommendation(intent, quotes={})

    assert error.value.code == "not_enough_supported_coins"


def test_raises_when_selected_coin_has_no_market_quote() -> None:
    service = AllocationService()
    intent = ParsedPortfolioIntent(
        budget_usd=Decimal("1000"),
        risk_level=RiskLevel.low,
    )
    quotes = {
        "BTC": quote("BTC", "80000"),
        "ETH": quote("ETH", "2000"),
    }

    with pytest.raises(MarketDataError) as error:
        service.build_recommendation(intent, quotes)

    assert error.value.code == "missing_market_quote"
    assert "PAXG" in error.value.message
