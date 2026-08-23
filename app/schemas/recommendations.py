from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field


class RiskLevel(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"


class RecommendationRequest(BaseModel):
    message: str = Field(min_length=1, examples=["I want to invest $1000 in low risk crypto."])


class ParsedPortfolioIntent(BaseModel):
    budget_usd: Decimal = Field(gt=0)
    risk_level: RiskLevel
    preferred_tickers: list[str] = Field(default_factory=list)
    excluded_tickers: list[str] = Field(default_factory=list)
    excluded_categories: list[str] = Field(default_factory=list)


class PortfolioAllocation(BaseModel):
    name: str
    ticker: str
    amount_usd: Decimal
    price_usd: Decimal
    quantity: Decimal
    description: str


class RecommendationResponse(BaseModel):
    request: ParsedPortfolioIntent
    summary: str
    allocations: list[PortfolioAllocation] = Field(min_length=3, max_length=5)
    total_allocated_usd: Decimal
    disclaimer: str
