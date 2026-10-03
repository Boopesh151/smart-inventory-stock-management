"""Pydantic v2 schemas for product request and response bodies.

Schemas sit between the API and the database:
- they validate incoming JSON
- they shape outgoing JSON
They are not the SQLAlchemy Product model.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _strip_required_text(value: str) -> str:
    """Remove extra spaces and reject blank strings."""
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("must not be empty or only whitespace")
    return cleaned


class ProductCreate(BaseModel):
    """JSON body used when creating a product (POST /products/)."""

    name: str = Field(..., min_length=1, max_length=150)
    sku: str = Field(..., min_length=1, max_length=50)
    category: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., ge=0, description="Current stock. Cannot be negative.")
    price: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    supplier: str = Field(..., min_length=1, max_length=150)
    minimum_stock_level: int = Field(
        ...,
        ge=0,
        description="Low-stock threshold. Cannot be negative.",
    )

    @field_validator("name", "sku", "category", "supplier")
    @classmethod
    def text_fields_must_not_be_blank(cls, value: str) -> str:
        return _strip_required_text(value)


class ProductUpdate(BaseModel):
    """JSON body used when replacing a product (PUT /products/{id}).

    PUT is a full update, so every product field is required.
    """

    name: str = Field(..., min_length=1, max_length=150)
    sku: str = Field(..., min_length=1, max_length=50)
    category: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., ge=0)
    price: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    supplier: str = Field(..., min_length=1, max_length=150)
    minimum_stock_level: int = Field(..., ge=0)

    @field_validator("name", "sku", "category", "supplier")
    @classmethod
    def text_fields_must_not_be_blank(cls, value: str) -> str:
        return _strip_required_text(value)


class ProductRead(BaseModel):
    """JSON returned for a single product."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sku: str
    category: str
    quantity: int
    price: Decimal
    supplier: str
    minimum_stock_level: int
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseModel):
    """Paginated list of products."""

    total: int
    skip: int
    limit: int
    items: list[ProductRead]
class StockTransactionCreate(BaseModel):
    """JSON body used for Stock In / Stock Out."""

    product_id: int = Field(..., gt=0)
    transaction_type: str = Field(..., description="IN or OUT")
    quantity: int = Field(..., gt=0)

    @field_validator("transaction_type")
    @classmethod
    def validate_transaction_type(cls, value: str) -> str:
        value = value.strip().upper()

        if value not in {"IN", "OUT"}:
            raise ValueError("transaction_type must be IN or OUT")

        return value


class StockTransactionRead(BaseModel):
    """JSON returned after a stock transaction."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    transaction_type: str
    quantity: int
    created_at: datetime


