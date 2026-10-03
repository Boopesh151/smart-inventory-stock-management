"""SQLAlchemy models (table definitions)."""

from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


def utc_now() -> datetime:
    """Return the current UTC time."""
    return datetime.now(timezone.utc)


class Product(Base):
    """A product stored in inventory."""

    __tablename__ = "products"

    __table_args__ = (
        UniqueConstraint("sku", name="uq_products_sku"),
        CheckConstraint(
            "quantity >= 0",
            name="ck_products_quantity_non_negative",
        ),
        CheckConstraint(
            "minimum_stock_level >= 0",
            name="ck_products_minimum_stock_level_non_negative",
        ),
        CheckConstraint(
            "price >= 0",
            name="ck_products_price_non_negative",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    sku: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    supplier: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    minimum_stock_level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    def __repr__(self) -> str:
        return f"<Product id={self.id} sku={self.sku!r} name={self.name!r}>"


class StockTransaction(Base):
    """Records stock-in and stock-out transactions."""

    __tablename__ = "stock_transactions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )
    transaction_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )




