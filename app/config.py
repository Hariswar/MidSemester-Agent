from __future__ import annotations

import os
from dataclasses import dataclass


def _to_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "ollama3:latest")
    shipping_api_base_url: str = os.getenv("SHIPPING_API_BASE_URL", "http://localhost:8001")
    shipping_api_timeout_seconds: int = int(os.getenv("SHIPPING_API_TIMEOUT_SECONDS", "8"))
    enable_web_context: bool = _to_bool(os.getenv("ENABLE_WEB_CONTEXT"), True)


settings = Settings()
