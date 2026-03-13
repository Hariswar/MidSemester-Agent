from __future__ import annotations

from fastapi import HTTPException

from app.data import DeliveryStatusResult
from app.services.llm_ollama import synthesize_delivery_response
from app.services.order_db import get_order
from app.services.shipping_api import get_shipping_update
from app.services.web_context import get_local_conditions


def run_delivery_status_workflow(order_id: str, query: str) -> DeliveryStatusResult:
    order = get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order {order_id} was not found")

    shipping_update = get_shipping_update(order.tracking_number)
    web_context = get_local_conditions(order.destination_city, order.destination_state)

    integrated_response = synthesize_delivery_response(
        user_query=query,
        order_context=order.model_dump(),
        shipping_context=shipping_update.model_dump(),
        web_context=web_context,
    )

    return DeliveryStatusResult(
        integrated_response=integrated_response,
        order=order,
        shipping_update=shipping_update,
        web_context=web_context,
    )
