from decimal import Decimal, ROUND_HALF_UP

from app.clients.market_data import MarketQuote
from app.core.errors import InvalidPortfolioRequestError, MarketDataError
from app.data.coin_catalog import COIN_CATALOG, CoinMetadata
from app.schemas.recommendations import (
    ParsedPortfolioIntent,
    PortfolioAllocation,
    RecommendationResponse,
    RiskLevel,
)


DISCLAIMER = "This is an educational portfolio suggestion, not financial advice."
CENT = Decimal("0.01")
TOKEN_QUANTITY = Decimal("0.00000001")


class AllocationService:
    def build_recommendation(
        self,
        intent: ParsedPortfolioIntent,
        quotes: dict[str, MarketQuote],
    ) -> RecommendationResponse:
        selected_coins = self.select_coins(intent)
        allocations = self._calculate_allocations(intent.budget_usd, selected_coins, quotes)

        return RecommendationResponse(
            request=intent,
            summary=self._build_summary(intent.risk_level),
            allocations=allocations,
            total_allocated_usd=sum(item.amount_usd for item in allocations),
            disclaimer=DISCLAIMER,
        )

    def get_required_tickers(self, intent: ParsedPortfolioIntent) -> list[str]:
        return [coin.ticker for coin in self.select_coins(intent)]

    def select_coins(self, intent: ParsedPortfolioIntent) -> list[CoinMetadata]:
        excluded_tickers = {ticker.upper() for ticker in intent.excluded_tickers}
        excluded_categories = {category.lower() for category in intent.excluded_categories}
        preferred_tickers = [ticker.upper() for ticker in intent.preferred_tickers]

        candidates = [
            coin
            for coin in COIN_CATALOG.values()
            if intent.risk_level in coin.risk_profiles
            and coin.ticker not in excluded_tickers
            and coin.categories.isdisjoint(excluded_categories)
        ]

        selected: list[CoinMetadata] = []
        for ticker in preferred_tickers:
            preferred_coin = next((coin for coin in candidates if coin.ticker == ticker), None)
            if preferred_coin and preferred_coin not in selected:
                selected.append(preferred_coin)

        target_size = self._target_size(intent.risk_level)
        for coin in candidates:
            if len(selected) == target_size:
                break
            if coin not in selected:
                selected.append(coin)

        if len(selected) < 3:
            raise InvalidPortfolioRequestError(
                code="not_enough_supported_coins",
                message="At least three supported coins are required after applying constraints.",
            )

        return selected

    def _calculate_allocations(
        self,
        budget_usd: Decimal,
        selected_coins: list[CoinMetadata],
        quotes: dict[str, MarketQuote],
    ) -> list[PortfolioAllocation]:
        total_weight = sum(coin.default_weight for coin in selected_coins)
        remaining_budget = budget_usd
        allocations: list[PortfolioAllocation] = []

        for index, coin in enumerate(selected_coins):
            quote = quotes.get(coin.ticker)
            if quote is None:
                raise MarketDataError(
                    code="missing_market_quote",
                    message=f"Missing market data for ticker {coin.ticker}.",
                )
            if quote.price_usd <= 0:
                raise MarketDataError(
                    code="invalid_market_quote",
                    message=f"Market price for ticker {coin.ticker} must be greater than zero.",
                )

            is_last = index == len(selected_coins) - 1
            if is_last:
                amount_usd = remaining_budget
            else:
                raw_amount = budget_usd * (coin.default_weight / total_weight)
                amount_usd = raw_amount.quantize(CENT, rounding=ROUND_HALF_UP)
                remaining_budget -= amount_usd

            quantity = (amount_usd / quote.price_usd).quantize(
                TOKEN_QUANTITY,
                rounding=ROUND_HALF_UP,
            )
            allocations.append(
                PortfolioAllocation(
                    name=coin.name,
                    ticker=coin.ticker,
                    amount_usd=amount_usd,
                    price_usd=quote.price_usd,
                    quantity=quantity,
                    description=coin.description,
                )
            )

        return allocations

    def _target_size(self, risk_level: RiskLevel) -> int:
        if risk_level == RiskLevel.low:
            return 3
        if risk_level == RiskLevel.medium:
            return 4
        return 5

    def _build_summary(self, risk_level: RiskLevel) -> str:
        summaries = {
            RiskLevel.low: "A conservative allocation focused on established crypto assets.",
            RiskLevel.medium: "A balanced allocation across established and growth-oriented assets.",
            RiskLevel.high: "An aggressive allocation with higher-volatility crypto assets.",
        }
        return summaries[risk_level]
