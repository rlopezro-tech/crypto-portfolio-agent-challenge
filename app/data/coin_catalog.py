from decimal import Decimal

from pydantic import BaseModel

from app.schemas.recommendations import RiskLevel


class CoinMetadata(BaseModel):
    ticker: str
    name: str
    categories: set[str]
    risk_profiles: set[RiskLevel]
    default_weight: Decimal
    description: str


COIN_CATALOG: dict[str, CoinMetadata] = {
    "BTC": CoinMetadata(
        ticker="BTC",
        name="Bitcoin",
        categories={"store_of_value", "large_cap"},
        risk_profiles={RiskLevel.low, RiskLevel.medium},
        default_weight=Decimal("0.45"),
        description="Bitcoin is the first and most widely recognized cryptocurrency.",
    ),
    "ETH": CoinMetadata(
        ticker="ETH",
        name="Ethereum",
        categories={"smart_contracts", "large_cap"},
        risk_profiles={RiskLevel.low, RiskLevel.medium},
        default_weight=Decimal("0.35"),
        description="Ethereum is a smart contract platform used by decentralized applications.",
    ),
    "PAXG": CoinMetadata(
        ticker="PAXG",
        name="Paxos Gold",
        categories={"commodity_backed", "large_cap"},
        risk_profiles={RiskLevel.low},
        default_weight=Decimal("0.20"),
        description="Paxos Gold is a token backed by physical gold reserves.",
    ),
    "SOL": CoinMetadata(
        ticker="SOL",
        name="Solana",
        categories={"smart_contracts", "layer_1"},
        risk_profiles={RiskLevel.medium, RiskLevel.high},
        default_weight=Decimal("0.25"),
        description="Solana is a high-throughput blockchain platform for decentralized apps.",
    ),
    "LINK": CoinMetadata(
        ticker="LINK",
        name="Chainlink",
        categories={"oracle", "infrastructure"},
        risk_profiles={RiskLevel.medium},
        default_weight=Decimal("0.15"),
        description="Chainlink provides decentralized oracle infrastructure for smart contracts.",
    ),
    "MATIC": CoinMetadata(
        ticker="MATIC",
        name="Polygon",
        categories={"scaling", "infrastructure"},
        risk_profiles={RiskLevel.medium},
        default_weight=Decimal("0.10"),
        description="Polygon is an Ethereum scaling ecosystem focused on lower-cost transactions.",
    ),
    "AVAX": CoinMetadata(
        ticker="AVAX",
        name="Avalanche",
        categories={"smart_contracts", "layer_1"},
        risk_profiles={RiskLevel.high},
        default_weight=Decimal("0.20"),
        description="Avalanche is a layer 1 blockchain focused on fast finality and custom subnets.",
    ),
    "ARB": CoinMetadata(
        ticker="ARB",
        name="Arbitrum",
        categories={"scaling", "layer_2"},
        risk_profiles={RiskLevel.high},
        default_weight=Decimal("0.15"),
        description="Arbitrum is an Ethereum layer 2 network designed to reduce transaction costs.",
    ),
    "DOGE": CoinMetadata(
        ticker="DOGE",
        name="Dogecoin",
        categories={"meme"},
        risk_profiles={RiskLevel.high},
        default_weight=Decimal("0.10"),
        description="Dogecoin is a meme-origin cryptocurrency with high volatility.",
    ),
    "PEPE": CoinMetadata(
        ticker="PEPE",
        name="Pepe",
        categories={"meme"},
        risk_profiles={RiskLevel.high},
        default_weight=Decimal("0.05"),
        description="Pepe is a meme token with speculative demand and high volatility.",
    ),
}
