from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.cart import Cart
from app.models.product import Product
from app.schemas.cart import CartAdd, CartUpdate, CartResponse
from app.core.dependencies import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


@router.post(
    "/",
    response_model=CartResponse,
    status_code=status.HTTP_201_CREATED
)
def add_to_cart(
    cart_data: CartAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    product = db.get(Product, cart_data.product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    if cart_data.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than 0"
        )

    existing_cart = db.scalar(
        select(Cart).where(
            Cart.user_id == current_user.id,
            Cart.product_id == cart_data.product_id
        )
    )

    if existing_cart:
        existing_cart.quantity += cart_data.quantity
        db.commit()
        db.refresh(existing_cart)
        return existing_cart

    new_cart = Cart(
        user_id=current_user.id,
        product_id=cart_data.product_id,
        quantity=cart_data.quantity
    )

    db.add(new_cart)
    db.commit()
    db.refresh(new_cart)

    return new_cart


@router.get(
    "/",
    response_model=list[CartResponse]
)
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    cart_items = db.scalars(
        select(Cart).where(
            Cart.user_id == current_user.id
        )
    ).all()

    return cart_items


@router.put(
    "/{cart_id}",
    response_model=CartResponse
)
def update_cart(
    cart_id: int,
    cart_data: CartUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if cart_data.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than 0"
        )

    cart_item = db.scalar(
        select(Cart).where(
            Cart.id == cart_id,
            Cart.user_id == current_user.id
        )
    )

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    cart_item.quantity = cart_data.quantity

    db.commit()
    db.refresh(cart_item)

    return cart_item


@router.delete(
    "/{cart_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_from_cart(
    cart_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    cart_item = db.scalar(
        select(Cart).where(
            Cart.id == cart_id,
            Cart.user_id == current_user.id
        )
    )

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    db.delete(cart_item)
    db.commit()

    return None