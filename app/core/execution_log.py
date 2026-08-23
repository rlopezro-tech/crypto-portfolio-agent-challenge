import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi.encoders import jsonable_encoder

from app.core.config import settings

SENSITIVE_KEYS = {
    "api_key",
    "authorization",
    "token",
    "secret",
    "password",
    "ai_api_key",
    "market_data_api_key",
}


class ExecutionLogRecorder:
    def __init__(self, log_dir: str, enabled: bool = True) -> None:
        self.log_dir = Path(log_dir)
        self.enabled = enabled

    def record(
        self,
        *,
        route: str,
        request: dict[str, Any],
        status: str,
        response: dict[str, Any] | None = None,
        error: dict[str, Any] | None = None,
        execution_id: str | None = None,
    ) -> str:
        execution_id = execution_id or str(uuid4())
        if not self.enabled:
            return execution_id

        now = datetime.now(UTC)
        event = {
            "execution_id": execution_id,
            "timestamp": now.isoformat(),
            "route": route,
            "status": status,
            "request": self._redact(request),
            "response": self._redact(response or {}),
            "error": self._redact(error or {}),
        }

        self.log_dir.mkdir(parents=True, exist_ok=True)
        log_file = self.log_dir / f"executions-{now.date().isoformat()}.jsonl"
        with log_file.open("a", encoding="utf-8") as file:
            file.write(json.dumps(jsonable_encoder(event), ensure_ascii=True) + "\n")

        return execution_id

    def _redact(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: "[REDACTED]" if key.lower() in SENSITIVE_KEYS else self._redact(item)
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [self._redact(item) for item in value]
        return value


execution_log_recorder = ExecutionLogRecorder(
    log_dir=settings.execution_log_dir,
    enabled=settings.execution_log_enabled,
)
