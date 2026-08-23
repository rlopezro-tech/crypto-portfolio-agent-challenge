from app.schemas.recommendations import ParsedPortfolioIntent


class PortfolioAgent:
    async def parse_intent(self, message: str) -> ParsedPortfolioIntent:
        raise NotImplementedError("Portfolio intent parsing is not implemented yet.")
