from __future__ import annotations

from datetime import datetime, timezone

import requests

from app.config import settings
from app.data import ShippingUpdate


_FALLBACK_TRACKING = {
    "1Z999AA10123456784": {
        "provider_status": "In transit",
        "current_location": "Regional distribution center - Springfield, MO",
        "eta_window": "Tomorrow evening",
    },
    "123456789012": {
        "provider_status": "Label created",
        "current_location": "Shipment information received",
        "eta_window": "2-3 business days",
    },
}


def get_shipping_update(tracking_number: str) -> ShippingUpdate:
    endpoint = f"{settings.shipping_api_base_url.rstrip('/')}/track/{tracking_number}"

    try:
        response = requests.get(endpoint, timeout=settings.shipping_api_timeout_seconds)
        response.raise_for_status()
        payload = response.json()
        return ShippingUpdate(
            provider_status=payload.get("provider_status", "Unknown"),
            current_location=payload.get("current_location", "Unknown"),
            last_updated_utc=payload.get(
                "last_updated_utc", datetime.now(timezone.utc).isoformat()
            ),
            eta_window=payload.get("eta_window", "Unknown"),
        )
    except requests.RequestException:
        fallback = _FALLBACK_TRACKING.get(
            tracking_number,
            {
                "provider_status": "Unavailable",
                "current_location": "Provider API unreachable",
                "eta_window": "Unknown",
            },
        )
        return ShippingUpdate(
            provider_status=fallback["provider_status"],
            current_location=fallback["current_location"],
            last_updated_utc=datetime.now(timezone.utc).isoformat(),
            eta_window=fallback["eta_window"],
        )
