from decimal import Decimal

from pydantic import BaseModel


class MarketQuote(BaseModel):
    ticker: str
    price_usd: Decimal
    source: str


class MarketDataClient:
    async def get_quotes(self, tickers: list[str]) -> dict[str, MarketQuote]:
        raise NotImplementedError("Market data client is not implemented yet.")
