from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.product import Product
from app.core.dependencies import require_admin

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.get("/")
def get_products(
    db: Session = Depends(get_db)
):
    return db.scalars(
        select(Product)
    ).all()


@router.get("/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.get(Product, product_id)

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED
)
def create_product(
    name: str,
    description: str | None = None,
    price: float = 0,
    stock: int = 0,
    images: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    product = Product(
        name=name,
        description=description,
        price=price,
        stock=stock,
        images=images
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


@router.put("/{product_id}")
def update_product(
    product_id: int,
    name: str,
    description: str | None = None,
    price: float = 0,
    stock: int = 0,
    images: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    product = db.get(Product, product_id)

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    product.name = name
    product.description = description
    product.price = price
    product.stock = stock
    product.images = images

    db.commit()
    db.refresh(product)

    return product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    product = db.get(Product, product_id)

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.delete(product)
    db.commit()

    return {
        "message": "Product deleted successfully"
    }