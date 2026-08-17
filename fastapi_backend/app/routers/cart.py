from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.cart import Cart
from app.models.product import Product
from app.models.user import User
from app.schemas.cart import (
    CartAdd,
    CartUpdate,
    CartRemove,
    CartResponse,
    CartSummary,
    CartItemCalculation,
)
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)


# =========================================================
# ADD PRODUCT TO CART
# POST /cart/add
# =========================================================

@router.post(
    "/add",
    response_model=CartResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_to_cart(
    cart_data: CartAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.get(Product, cart_data.product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    if cart_data.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than 0",
        )

    if cart_data.quantity > product.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough stock available",
        )

    existing_cart = db.scalar(
        select(Cart).where(
            Cart.user_id == current_user.id,
            Cart.product_id == cart_data.product_id,
        )
    )

    if existing_cart:
        new_quantity = (
            existing_cart.quantity + cart_data.quantity
        )

        if new_quantity > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not enough stock available",
            )

        existing_cart.quantity = new_quantity

        db.commit()
        db.refresh(existing_cart)

        return existing_cart

    new_cart = Cart(
        user_id=current_user.id,
        product_id=cart_data.product_id,
        quantity=cart_data.quantity,
    )

    db.add(new_cart)
    db.commit()
    db.refresh(new_cart)

    return new_cart


# =========================================================
# VIEW CART
# GET /cart
# =========================================================

@router.get(
    "",
    response_model=list[CartResponse],
)
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart_items = db.scalars(
        select(Cart).where(
            Cart.user_id == current_user.id
        )
    ).all()

    return cart_items


# =========================================================
# UPDATE CART QUANTITY
# PUT /cart/update
# =========================================================

@router.put(
    "/update",
    response_model=CartResponse,
)
def update_cart(
    cart_data: CartUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if cart_data.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than 0",
        )

    product = db.get(Product, cart_data.product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    if cart_data.quantity > product.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough stock available",
        )

    cart_item = db.scalar(
        select(Cart).where(
            Cart.product_id == cart_data.product_id,
            Cart.user_id == current_user.id,
        )
    )

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found in cart",
        )

    cart_item.quantity = cart_data.quantity

    db.commit()
    db.refresh(cart_item)

    return cart_item


# =========================================================
# REMOVE PRODUCT FROM CART
# DELETE /cart/remove
# =========================================================

@router.delete(
    "/remove",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_from_cart(
    cart_data: CartRemove,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart_item = db.scalar(
        select(Cart).where(
            Cart.product_id == cart_data.product_id,
            Cart.user_id == current_user.id,
        )
    )

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found in cart",
        )

    db.delete(cart_item)
    db.commit()

    return None


# =========================================================
# CART CALCULATIONS
# GET /cart/summary
# =========================================================

@router.get(
    "/summary",
    response_model=CartSummary,
)
def get_cart_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart_items = db.scalars(
        select(Cart).where(
            Cart.user_id == current_user.id
        )
    ).all()

    items = []
    cart_total = 0.0

    for cart_item in cart_items:

        product = db.get(Product, cart_item.product_id)

        if not product:
            continue

        # Item total = product price × quantity
        item_total = product.price * cart_item.quantity

        cart_total += item_total

        items.append(
            CartItemCalculation(
                id=cart_item.id,
                product_id=product.id,
                product_name=product.name,
                price=product.price,
                quantity=cart_item.quantity,
                item_total=item_total,
            )
        )

    # Tax is optional
    tax = 0.0

    # Grand total = cart total + tax
    grand_total = cart_total + tax

    return CartSummary(
        items=items,
        cart_total=cart_total,
        tax=tax,
        grand_total=grand_total,
    )