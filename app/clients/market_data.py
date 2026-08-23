from decimal import Decimal

import httpx
from pydantic import BaseModel

from app.core.config import settings
from app.core.errors import MarketDataError
from app.data.coin_catalog import COIN_CATALOG


class MarketQuote(BaseModel):
    ticker: str
    price_usd: Decimal
    source: str
    market_cap_usd: Decimal | None = None
    last_updated: str | None = None


class MarketDataClient:
    async def get_quotes(self, tickers: list[str]) -> dict[str, MarketQuote]:
        raise NotImplementedError("Market data client is not implemented yet.")


class DemoMarketDataClient(MarketDataClient):
    demo_prices: dict[str, Decimal] = {
        "BTC": Decimal("80000"),
        "ETH": Decimal("2000"),
        "PAXG": Decimal("3400"),
        "SOL": Decimal("150"),
        "LINK": Decimal("20"),
        "MATIC": Decimal("0.80"),
        "AVAX": Decimal("40"),
        "ARB": Decimal("2"),
        "DOGE": Decimal("0.12"),
        "PEPE": Decimal("0.000012"),
    }

    async def get_quotes(self, tickers: list[str]) -> dict[str, MarketQuote]:
        normalized_tickers = _normalize_tickers(tickers)
        missing_tickers = [ticker for ticker in normalized_tickers if ticker not in self.demo_prices]
        if missing_tickers:
            raise MarketDataError(
                code="unsupported_demo_ticker",
                message=f"Demo market data is unavailable for: {', '.join(missing_tickers)}.",
            )

        return {
            ticker: MarketQuote(ticker=ticker, price_usd=self.demo_prices[ticker], source="demo")
            for ticker in normalized_tickers
        }


class CoinMarketCapMarketDataClient(MarketDataClient):
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://pro-api.coinmarketcap.com",
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.http_client = http_client

    async def get_quotes(self, tickers: list[str]) -> dict[str, MarketQuote]:
        if not self.api_key:
            raise MarketDataError(
                code="missing_market_data_api_key",
                message="MARKET_DATA_API_KEY is required when MARKET_DATA_PROVIDER=coinmarketcap.",
            )

        normalized_tickers = _normalize_tickers(tickers)
        id_to_ticker = self._build_id_lookup(normalized_tickers)
        if not id_to_ticker:
            raise MarketDataError(
                code="unsupported_market_ticker",
                message="No supported CoinMarketCap tickers were requested.",
            )

        payload = await self._request_quotes(ids=list(id_to_ticker))
        return self._parse_quotes(payload, id_to_ticker)

    async def _request_quotes(self, ids: list[int]) -> dict:
        params = {
            "id": ",".join(str(cmc_id) for cmc_id in ids),
            "convert": "USD",
        }
        headers = {
            "Accept": "application/json",
            "X-CMC_PRO_API_KEY": self.api_key,
        }

        if self.http_client is not None:
            response = await self.http_client.get(
                f"{self.base_url}/v3/cryptocurrency/quotes/latest",
                params=params,
                headers=headers,
            )
        else:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/v3/cryptocurrency/quotes/latest",
                    params=params,
                    headers=headers,
                )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise MarketDataError(
                code="coinmarketcap_http_error",
                message=f"CoinMarketCap request failed with status {exc.response.status_code}.",
            ) from exc

        data = response.json()
        status = data.get("status", {})
        if str(status.get("error_code", "0")) != "0":
            raise MarketDataError(
                code="coinmarketcap_api_error",
                message=status.get("error_message") or "CoinMarketCap returned an API error.",
            )
        return data

    def _build_id_lookup(self, tickers: list[str]) -> dict[int, str]:
        id_to_ticker: dict[int, str] = {}
        unsupported_tickers = []
        for ticker in tickers:
            coin = COIN_CATALOG.get(ticker)
            if coin is None:
                unsupported_tickers.append(ticker)
                continue
            id_to_ticker[coin.cmc_id] = ticker

        if unsupported_tickers:
            raise MarketDataError(
                code="unsupported_market_ticker",
                message=f"Unsupported market data tickers: {', '.join(unsupported_tickers)}.",
            )
        return id_to_ticker

    def _parse_quotes(self, payload: dict, id_to_ticker: dict[int, str]) -> dict[str, MarketQuote]:
        raw_data = payload.get("data")
        if not raw_data:
            raise MarketDataError(
                code="invalid_coinmarketcap_response",
                message="CoinMarketCap response did not include quote data.",
            )

        records = raw_data.values() if isinstance(raw_data, dict) else raw_data
        quotes: dict[str, MarketQuote] = {}
        for record in records:
            cmc_id = int(record["id"])
            ticker = id_to_ticker.get(cmc_id)
            usd_quote = _extract_usd_quote(record.get("quote"))
            price = usd_quote.get("price")
            if ticker is None or price is None:
                continue
            quotes[ticker] = MarketQuote(
                ticker=ticker,
                price_usd=Decimal(str(price)),
                market_cap_usd=_optional_decimal(usd_quote.get("market_cap")),
                last_updated=usd_quote.get("last_updated") or record.get("last_updated"),
                source="coinmarketcap",
            )

        missing_tickers = sorted(set(id_to_ticker.values()) - set(quotes))
        if missing_tickers:
            raise MarketDataError(
                code="missing_coinmarketcap_quotes",
                message=f"CoinMarketCap did not return quotes for: {', '.join(missing_tickers)}.",
            )
        return quotes


def create_market_data_client() -> MarketDataClient:
    provider = settings.market_data_provider.lower()
    if provider in {"coinmarketcap", "cmc"}:
        return CoinMarketCapMarketDataClient(
            api_key=settings.market_data_api_key,
            base_url=settings.market_data_base_url,
        )
    if provider == "demo":
        return DemoMarketDataClient()
    raise MarketDataError(
        code="unsupported_market_data_provider",
        message=f"Unsupported market data provider: {settings.market_data_provider}.",
    )


def _normalize_tickers(tickers: list[str]) -> list[str]:
    return sorted({ticker.strip().upper() for ticker in tickers if ticker.strip()})


def _optional_decimal(value: object) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def _extract_usd_quote(raw_quote: object) -> dict:
    if isinstance(raw_quote, dict):
        return raw_quote.get("USD", {})
    if isinstance(raw_quote, list):
        return next(
            (
                quote
                for quote in raw_quote
                if isinstance(quote, dict) and quote.get("symbol") == "USD"
            ),
            {},
        )
    return {}
