from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    popularity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    price: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    stock: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    images: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # =====================================================
    # PRODUCT → CART RELATIONSHIP
    # One product can appear in many cart items
    # =====================================================

    cart_items = relationship(
        "Cart",
        back_populates="product"
    )