from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DeliveryStatusRequest(BaseModel):
    order_id: str = Field(..., examples=["ORDER-1001"])
    query: str = Field(
        default="Can you tell me the delivery status of my order?",
        examples=["Can you tell me the delivery status of my order?"],
    )


class OrderRecord(BaseModel):
    order_id: str
    customer_name: str
    carrier: str
    tracking_number: str
    destination_city: str
    destination_state: str
    expected_delivery_date: str
    status: str


class ShippingUpdate(BaseModel):
    provider_status: str
    current_location: str
    last_updated_utc: str
    eta_window: str


class DeliveryStatusResult(BaseModel):
    integrated_response: str
    order: OrderRecord
    shipping_update: ShippingUpdate
    web_context: dict[str, Any] | None = None
