from __future__ import annotations

import json
import logging
import time
from collections import Counter
from typing import Any

logger = logging.getLogger("chainbreaker")
METRICS: Counter[str] = Counter()


def configure_logging() -> None:
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)


def increment(metric: str, value: int = 1) -> None:
    METRICS[metric] += value


def structured_log(event: str, **fields: Any) -> None:
    safe = {key: value for key, value in fields.items() if key not in {"password", "token", "secret", "raw_event", "content"}}
    logger.info(json.dumps({"event": event, **safe}, default=str, sort_keys=True))


def observe_request(method: str, path: str, status: int, elapsed_seconds: float) -> None:
    increment("api_requests_total")
    increment(f"api_status_{status}")
    structured_log("api_request", method=method, path=path, status=status, elapsed_ms=round(elapsed_seconds * 1000, 2))
