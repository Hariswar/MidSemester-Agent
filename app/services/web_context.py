from __future__ import annotations

import requests

from app.config import settings


def get_local_conditions(city: str, state: str) -> dict | None:
    if not settings.enable_web_context:
        return None

    location = f"{city}, {state}"
    endpoint = f"https://wttr.in/{location}?format=j1"
    try:
        response = requests.get(endpoint, timeout=6)
        response.raise_for_status()
        payload = response.json()
        current = payload.get("current_condition", [{}])[0]
        description = current.get("weatherDesc", [{}])[0].get("value", "Unknown")

        lowered = description.lower()
        risk = "normal"
        if "storm" in lowered or "snow" in lowered or "ice" in lowered:
            risk = "possible delay"

        return {
            "location": location,
            "weather": description,
            "temperature_c": current.get("temp_C", "Unknown"),
            "logistics_risk": risk,
        }
    except requests.RequestException:
        return {
            "location": location,
            "weather": "Unavailable",
            "temperature_c": "Unknown",
            "logistics_risk": "unknown",
        }
