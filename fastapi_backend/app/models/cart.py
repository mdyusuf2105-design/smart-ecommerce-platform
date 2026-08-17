from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Cart(Base):
    __tablename__ = "cart"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )

    # =====================================================
    # CART → USER
    # Many cart items belong to one user
    # =====================================================

    user = relationship(
        "User",
        back_populates="cart_items"
    )

    # =====================================================
    # CART → PRODUCT
    # Many cart items can refer to one product
    # =====================================================

    product = relationship(
        "Product",
        back_populates="cart_items"
    )