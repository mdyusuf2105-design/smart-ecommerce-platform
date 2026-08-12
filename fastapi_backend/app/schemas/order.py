from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OrderCreate(BaseModel):
    product_id: int
    quantity: int


class OrderResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    total_price: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)