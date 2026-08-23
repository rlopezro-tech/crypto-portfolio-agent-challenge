from pydantic import BaseModel

from app.schemas.recommendations import RiskLevel


class CoinMetadata(BaseModel):
    ticker: str
    name: str
    categories: set[str]
    risk_profiles: set[RiskLevel]
    description: str


COIN_CATALOG: dict[str, CoinMetadata] = {}
