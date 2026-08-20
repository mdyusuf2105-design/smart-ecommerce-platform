import os

import stripe
from dotenv import load_dotenv

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


load_dotenv()

router = APIRouter(
    prefix="/checkout",
    tags=["Checkout"],
)


@router.post("")
def checkout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # =====================================================
    # 1. Get user's cart
    # =====================================================

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

    # =====================================================
    # 2. Validate cart and calculate total
    # =====================================================

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

    # =====================================================
    # 3. Create Order
    # =====================================================

    order = Order(
        user_id=current_user.id,
        total=total_price,
        payment_status="pending",
        order_status="pending",
    )

    db.add(order)
    db.flush()

    # =====================================================
    # 4. Create Order Items
    # =====================================================

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

    order_id = order.id

    # =====================================================
    # 5. Stripe configuration
    # =====================================================

    stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")

    if not stripe_secret_key:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stripe secret key is not configured",
        )

    stripe.api_key = stripe_secret_key

    # =====================================================
    # 6. Create Stripe Checkout Session
    # =====================================================

    try:

        line_items = []

        for item in validated_items:

            product = item["product"]

            line_items.append({
                "price_data": {
                    "currency": "inr",
                    "product_data": {
                        "name": product.name,
                    },
                    "unit_amount": int(
                        product.price * 100
                    ),
                },
                "quantity": item["quantity"],
            })

        checkout_session = stripe.checkout.Session.create(
            mode="payment",

            line_items=line_items,

            success_url=(
                "http://localhost:5173/payment-success"
            ),

            cancel_url=(
                "http://localhost:5173/payment-cancelled"
            ),

            # Metadata on Checkout Session
            metadata={
                "order_id": str(order_id),
                "user_id": str(current_user.id),
            },

            # Metadata on the PaymentIntent automatically
            # created by Stripe Checkout
            payment_intent_data={
                "metadata": {
                    "order_id": str(order_id),
                    "user_id": str(current_user.id),
                }
            },
        )

        # =================================================
        # 7. Create Payment Record
        # =================================================

        # We temporarily store the Checkout Session ID.
        # The webhook will replace it with the real
        # PaymentIntent ID after successful payment.

        payment = Payment(
            order_id=order_id,
            amount=total_price,
            payment_method="stripe",
            transaction_id=checkout_session.id,
            status="pending",
        )

        db.add(payment)

        # =================================================
        # 8. Commit
        # =================================================

        db.commit()

        # =================================================
        # 9. Return response
        # =================================================

        return {
            "message": "Checkout session created successfully",
            "order_id": order_id,
            "amount": total_price,
            "currency": "INR",
            "payment_status": "pending",
            "order_status": "pending",
            "checkout_session_id": checkout_session.id,
            "checkout_url": checkout_session.url,
        }

    except stripe.StripeError as e:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )