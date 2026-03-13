from __future__ import annotations

import requests

from app.config import settings


def synthesize_delivery_response(
    *,
    user_query: str,
    order_context: dict,
    shipping_context: dict,
    web_context: dict | None,
) -> str:
    system_prompt = (
        "You are a logistics assistant. Produce a concise, actionable response with current "
        "delivery status, ETA, and one next-best action if delays are possible."
    )

    user_prompt = (
        f"User question: {user_query}\n\n"
        f"Order management data: {order_context}\n"
        f"Shipping provider live update: {shipping_context}\n"
        f"Optional local context: {web_context}\n\n"
        "Write 2-3 sentences max."
    )

    payload = {
        "model": settings.ollama_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
    }

    endpoint = f"{settings.ollama_base_url.rstrip('/')}/api/chat"
    try:
        response = requests.post(endpoint, json=payload, timeout=40)
        response.raise_for_status()
        body = response.json()
        content = body.get("message", {}).get("content", "").strip()
        if content:
            return content
    except requests.RequestException:
        pass

    # Deterministic fallback if Ollama is unavailable.
    provider_status = shipping_context.get("provider_status", "Unknown")
    eta_window = shipping_context.get("eta_window", "Unknown")
    current_location = shipping_context.get("current_location", "Unknown")
    return (
        f"Your package is currently {provider_status.lower()} and expected {eta_window.lower()}. "
        f"Live tracking indicates it is at {current_location}."
    )
