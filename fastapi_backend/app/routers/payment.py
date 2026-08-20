import os

import stripe

from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.payment import Payment
from app.models.order import Order


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@router.post("/webhook")
async def stripe_webhook(request: Request):

    payload = await request.body()

    stripe_signature = request.headers.get("stripe-signature")

    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    if not webhook_secret:
        raise HTTPException(
            status_code=500,
            detail="Stripe webhook secret is not configured",
        )

    try:
        event = stripe.Webhook.construct_event(
            payload,
            stripe_signature,
            webhook_secret,
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid payload",
        )

    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=400,
            detail="Invalid Stripe signature",
        )

    # =====================================================
    # PAYMENT INTENT SUCCEEDED
    # =====================================================

    if event["type"] == "payment_intent.succeeded":

        payment_intent = event["data"]["object"]

        payment_intent_id = payment_intent.id

        metadata = payment_intent.metadata.to_dict()

        order_id = metadata.get("order_id")

        if not order_id:
            return {
                "received": True
            }

        db: Session = SessionLocal()

        try:

            payment = (
                db.query(Payment)
                .filter(
                    Payment.order_id == int(order_id)
                )
                .first()
            )

            if payment:

                payment.transaction_id = payment_intent_id
                payment.status = "paid"

                order = (
                    db.query(Order)
                    .filter(
                        Order.id == payment.order_id
                    )
                    .first()
                )

                if order:
                    order.payment_status = "paid"
                    order.order_status = "paid"

                db.commit()

        finally:
            db.close()

    return {
        "received": True
    }
