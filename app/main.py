from __future__ import annotations

import json

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.data import DeliveryStatusRequest, DeliveryStatusResult
from app.services.order_db import init_db
from app.workflow import run_delivery_status_workflow


class PrettyJSONResponse(JSONResponse):
    def render(self, content: object) -> bytes:
        formatted = json.dumps(content, indent=2, ensure_ascii=True)
        return f"{formatted}\n".encode("utf-8")


app = FastAPI(
    title="Single-Agent Delivery Status Assistant",
    version="1.0.0",
    default_response_class=PrettyJSONResponse,
)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/delivery-status", response_model=DeliveryStatusResult)
def delivery_status(request: DeliveryStatusRequest) -> DeliveryStatusResult:
    return run_delivery_status_workflow(request.order_id, request.query)
