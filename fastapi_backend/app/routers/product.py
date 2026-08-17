from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.product import Product
from app.core.dependencies import require_admin


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# =========================================================
# GET ALL PRODUCTS + FILTERS
# =========================================================

@router.get("/")
def get_products(
    category: str | None = None,
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    min_popularity: int | None = Query(None, ge=0),
    in_stock: bool | None = None,
    db: Session = Depends(get_db)
):
    query = select(Product)

    # Category filter
    if category:
        query = query.where(
            Product.category == category
        )

    # Minimum price filter
    if min_price is not None:
        query = query.where(
            Product.price >= min_price
        )

    # Maximum price filter
    if max_price is not None:
        query = query.where(
            Product.price <= max_price
        )

    # Popularity filter
    if min_popularity is not None:
        query = query.where(
            Product.popularity >= min_popularity
        )

    # Stock availability filter
    if in_stock is True:
        query = query.where(
            Product.stock > 0
        )

    elif in_stock is False:
        query = query.where(
            Product.stock == 0
        )

    return db.scalars(query).all()


# =========================================================
# GET PRODUCTS BY CATEGORY
# =========================================================

@router.get("/category/{category}")
def get_products_by_category(
    category: str,
    db: Session = Depends(get_db)
):
    products = db.scalars(
        select(Product).where(
            Product.category == category
        )
    ).all()

    return products


# =========================================================
# GET SINGLE PRODUCT
# =========================================================

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


# =========================================================
# CREATE PRODUCT
# =========================================================

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED
)
def create_product(
    name: str,
    category: str | None = None,
    description: str | None = None,
    price: float = 0,
    stock: int = 0,
    popularity: int = 0,
    images: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    product = Product(
        name=name,
        category=category,
        description=description,
        price=price,
        stock=stock,
        popularity=popularity,
        images=images
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


# =========================================================
# UPDATE PRODUCT
# =========================================================

@router.put("/{product_id}")
def update_product(
    product_id: int,
    name: str,
    category: str | None = None,
    description: str | None = None,
    price: float = 0,
    stock: int = 0,
    popularity: int = 0,
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
    product.category = category
    product.description = description
    product.price = price
    product.stock = stock
    product.popularity = popularity
    product.images = images

    db.commit()
    db.refresh(product)

    return product


# =========================================================
# DELETE PRODUCT
# =========================================================

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