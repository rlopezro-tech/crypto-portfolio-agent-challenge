from decimal import Decimal

import httpx
import pytest

from app.clients.market_data import CoinMarketCapMarketDataClient, DemoMarketDataClient
from app.core.errors import MarketDataError


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_demo_market_data_client_returns_supported_quotes() -> None:
    client = DemoMarketDataClient()

    quotes = await client.get_quotes(["BTC", "ETH"])

    assert quotes["BTC"].price_usd == Decimal("80000")
    assert quotes["BTC"].source == "demo"
    assert quotes["ETH"].price_usd == Decimal("2000")


@pytest.mark.anyio
async def test_coinmarketcap_client_parses_v3_quotes_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v3/cryptocurrency/quotes/latest"
        assert request.url.params["id"] == "1,1027"
        assert request.url.params["convert"] == "USD"
        assert request.headers["X-CMC_PRO_API_KEY"] == "test-key"
        return httpx.Response(
            200,
            json={
                "status": {"error_code": 0, "error_message": ""},
                "data": [
                    {
                        "id": 1,
                        "name": "Bitcoin",
                        "symbol": "BTC",
                        "quote": {
                            "USD": {
                                "price": 80123.45,
                                "market_cap": 1580000000000,
                                "last_updated": "2026-08-23T22:00:00.000Z",
                            }
                        },
                    },
                    {
                        "id": 1027,
                        "name": "Ethereum",
                        "symbol": "ETH",
                        "quote": {"USD": {"price": 2100.12}},
                    },
                ],
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://pro-api.coinmarketcap.com",
    ) as http_client:
        client = CoinMarketCapMarketDataClient(
            api_key="test-key",
            http_client=http_client,
        )

        quotes = await client.get_quotes(["ETH", "BTC"])

    assert quotes["BTC"].price_usd == Decimal("80123.45")
    assert quotes["BTC"].market_cap_usd == Decimal("1580000000000")
    assert quotes["BTC"].last_updated == "2026-08-23T22:00:00.000Z"
    assert quotes["BTC"].source == "coinmarketcap"
    assert quotes["ETH"].price_usd == Decimal("2100.12")


@pytest.mark.anyio
async def test_coinmarketcap_client_requires_api_key() -> None:
    client = CoinMarketCapMarketDataClient(api_key="")

    with pytest.raises(MarketDataError) as error:
        await client.get_quotes(["BTC"])

    assert error.value.code == "missing_market_data_api_key"
