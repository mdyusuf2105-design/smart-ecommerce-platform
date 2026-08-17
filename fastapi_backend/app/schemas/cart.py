from pydantic import BaseModel


class CartAdd(BaseModel):
    product_id: int
    quantity: int = 1


class CartUpdate(BaseModel):
    product_id: int
    quantity: int


class CartRemove(BaseModel):
    product_id: int


class CartResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True


# Cart calculation response
class CartItemCalculation(BaseModel):
    id: int
    product_id: int
    product_name: str
    price: float
    quantity: int
    item_total: float


class CartSummary(BaseModel):
    items: list[CartItemCalculation]
    cart_total: float
    tax: float
    grand_total: float