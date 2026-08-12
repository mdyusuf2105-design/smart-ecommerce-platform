from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


# Customer can place an order
@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Only customers can place orders
    if current_user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can place orders"
        )

    # Find product
    product = db.get(
        Product,
        order_data.product_id
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Validate quantity
    if order_data.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than 0"
        )

    # Check stock
    if product.stock < order_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient stock"
        )

    # Calculate total
    total_price = product.price * order_data.quantity

    # Create order
    order = Order(
        user_id=current_user.id,
        product_id=product.id,
        quantity=order_data.quantity,
        total_price=total_price
    )

    # Reduce stock
    product.stock -= order_data.quantity

    db.add(order)
    db.commit()
    db.refresh(order)

    return order


# Customer can view their own orders
@router.get(
    "/",
    response_model=list[OrderResponse]
)
def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    orders = db.scalars(
        select(Order).where(
            Order.user_id == current_user.id
        )
    ).all()

    return orders