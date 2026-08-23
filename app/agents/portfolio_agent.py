import json
import re
from decimal import Decimal
from json import JSONDecodeError

from pydantic import ValidationError

from app.agents.prompts import PORTFOLIO_INTENT_SYSTEM_PROMPT
from app.core.config import settings
from app.core.errors import InvalidPortfolioRequestError
from app.data.coin_catalog import COIN_CATALOG
from app.schemas.recommendations import ParsedPortfolioIntent, RiskLevel


class PortfolioAgent:
    def __init__(self, use_ai: bool | None = None) -> None:
        self.use_ai = settings.ai_api_key != "" if use_ai is None else use_ai

    async def parse_intent(self, message: str) -> ParsedPortfolioIntent:
        if self.use_ai and settings.ai_api_key:
            try:
                return await self._parse_with_ai(message)
            except (ImportError, ValidationError, Exception):
                return self._parse_with_fallback(message)

        return self._parse_with_fallback(message)

    async def _parse_with_ai(self, message: str) -> ParsedPortfolioIntent:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            api_key=settings.ai_api_key,
            base_url=settings.ai_base_url,
        )
        completion = await client.chat.completions.create(
            model=settings.ai_model,
            messages=[
                {
                    "role": "system",
                    "content": PORTFOLIO_INTENT_SYSTEM_PROMPT,
                },
                {"role": "user", "content": message},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        content = completion.choices[0].message.content or ""
        intent = ParsedPortfolioIntent.model_validate(_loads_json_content(content))
        return self._normalize_intent(intent)

    def _parse_with_fallback(self, message: str) -> ParsedPortfolioIntent:
        normalized_message = message.lower()
        return ParsedPortfolioIntent(
            budget_usd=self._extract_budget(normalized_message),
            risk_level=self._extract_risk_level(normalized_message),
            preferred_tickers=self._extract_preferred_tickers(message),
            excluded_tickers=self._extract_excluded_tickers(message),
            excluded_categories=self._extract_excluded_categories(normalized_message),
        )

    def _extract_budget(self, message: str) -> Decimal:
        patterns = [
            r"\$\s*([0-9][0-9,]*(?:\.[0-9]+)?)",
            r"([0-9][0-9,]*(?:\.[0-9]+)?)\s*(?:usd|dollars?)",
            r"invest\s+([0-9][0-9,]*(?:\.[0-9]+)?)",
        ]
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return Decimal(match.group(1).replace(",", ""))

        raise InvalidPortfolioRequestError(
            code="missing_budget",
            message="Please include a budget, for example: $1000.",
        )

    def _extract_risk_level(self, message: str) -> RiskLevel:
        for risk_level in RiskLevel:
            if risk_level.value in message:
                return risk_level

        raise InvalidPortfolioRequestError(
            code="missing_risk_level",
            message="Please include a risk level: low, medium, or high.",
        )

    def _extract_preferred_tickers(self, message: str) -> list[str]:
        preferred_tickers: list[str] = []
        for pattern in (r"prefer\s+([A-Za-z0-9,\s]+)", r"include\s+([A-Za-z0-9,\s]+)"):
            for match in re.finditer(pattern, message, flags=re.IGNORECASE):
                preferred_tickers.extend(self._known_tickers_in_text(match.group(1)))
        return _dedupe(preferred_tickers)

    def _extract_excluded_tickers(self, message: str) -> list[str]:
        excluded_tickers: list[str] = []
        for pattern in (r"exclude\s+([A-Za-z0-9,\s]+)", r"without\s+([A-Za-z0-9,\s]+)"):
            for match in re.finditer(pattern, message, flags=re.IGNORECASE):
                excluded_tickers.extend(self._known_tickers_in_text(match.group(1)))
        return _dedupe(excluded_tickers)

    def _extract_excluded_categories(self, message: str) -> list[str]:
        if "exclude meme" in message or "without meme" in message or "no meme" in message:
            return ["meme"]
        return []

    def _known_tickers_in_text(self, text: str) -> list[str]:
        upper_text = text.upper()
        return [ticker for ticker in COIN_CATALOG if re.search(rf"\b{ticker}\b", upper_text)]

    def _normalize_intent(self, intent: ParsedPortfolioIntent) -> ParsedPortfolioIntent:
        return ParsedPortfolioIntent(
            budget_usd=intent.budget_usd,
            risk_level=intent.risk_level,
            preferred_tickers=_dedupe([ticker.upper() for ticker in intent.preferred_tickers]),
            excluded_tickers=_dedupe([ticker.upper() for ticker in intent.excluded_tickers]),
            excluded_categories=_dedupe(
                [_normalize_category(category) for category in intent.excluded_categories]
            ),
        )


def _dedupe(values: list[str]) -> list[str]:
    deduped: list[str] = []
    for value in values:
        if value and value not in deduped:
            deduped.append(value)
    return deduped


def _normalize_category(category: str) -> str:
    normalized = category.lower().strip()
    if normalized in {"meme coin", "meme coins", "memecoin", "memecoins"}:
        return "meme"
    return normalized


def _loads_json_content(content: str) -> dict:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        payload = json.loads(cleaned)
    except JSONDecodeError as error:
        raise ValidationError.from_exception_data(
            "ParsedPortfolioIntent",
            [
                {
                    "type": "value_error",
                    "loc": ("ai_response",),
                    "msg": "AI response was not valid JSON",
                    "input": content,
                    "ctx": {"error": error},
                }
            ],
        ) from error

    if not isinstance(payload, dict):
        raise ValidationError.from_exception_data(
            "ParsedPortfolioIntent",
            [
                {
                    "type": "dict_type",
                    "loc": ("ai_response",),
                    "msg": "AI response JSON must be an object",
                    "input": payload,
                }
            ],
        )

    return payload
