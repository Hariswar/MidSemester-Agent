from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException

app = FastAPI(title="Mock Shipping Provider API", version="1.0.0")

TRACKING_UPDATES = {
    "1Z999AA10123456784": {
        "provider_status": "In transit",
        "current_location": "Regional distribution center - Springfield, MO",
        "eta_window": "Tomorrow evening",
    },
    "123456789012": {
        "provider_status": "Label created",
        "current_location": "Origin facility - Kansas City, MO",
        "eta_window": "2-3 business days",
    },
}


@app.get("/track/{tracking_number}")
def track(tracking_number: str) -> dict:
    update = TRACKING_UPDATES.get(tracking_number)
    if update is None:
        raise HTTPException(status_code=404, detail="Tracking number not found")

    return {
        **update,
        "last_updated_utc": datetime.now(timezone.utc).isoformat(),
    }
