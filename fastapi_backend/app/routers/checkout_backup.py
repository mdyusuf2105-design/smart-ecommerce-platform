from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import get_current_user

from app.models.cart import Cart
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.payment import Payment
from app.models.user import User


router = APIRouter(
    prefix="/checkout",
    tags=["Checkout"],
)


@router.post("")
def checkout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Get user's cart
    cart_items = db.scalars(
        select(Cart).where(
            Cart.user_id == current_user.id
        )
    ).all()

    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty",
        )

    # 2. Validate cart and calculate total
    total_price = 0.0
    validated_items = []

    for cart_item in cart_items:

        product = db.get(
            Product,
            cart_item.product_id
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {cart_item.product_id} not found",
            )

        if cart_item.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid cart quantity",
            )

        if cart_item.quantity > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for {product.name}",
            )

        item_total = product.price * cart_item.quantity

        total_price += item_total

        validated_items.append({
            "product": product,
            "quantity": cart_item.quantity,
            "item_total": item_total,
        })

    # 3. Create one order
    order = Order(
        user_id=current_user.id,
        total=total_price,
        payment_status="pending",
        order_status="pending",
    )

    db.add(order)
    db.flush()

    # 4. Create order items
    for item in validated_items:

        order_item = OrderItem(
            order_id=order.id,
            product_id=item["product"].id,
            quantity=item["quantity"],
            price=item["product"].price,
            item_total=item["item_total"],
        )

        db.add(order_item)

    db.flush()

    # 5. Create mock payment
    transaction_id = f"mock_txn_{order.id}"

    payment = Payment(
        order_id=order.id,
        amount=total_price,
        payment_method="mock_stripe",
        transaction_id=transaction_id,
        status="pending",
    )

    db.add(payment)

    # 6. Commit everything
    db.commit()

    # 7. Return mock checkout response
    return {
        "message": "Checkout initialized successfully",
        "order_id": order.id,
        "amount": total_price,
        "currency": "INR",
        "payment_status": "pending",
        "order_status": "pending",
        "transaction_id": transaction_id,
        "checkout_url": "https://checkout.stripe.com/example"
    }