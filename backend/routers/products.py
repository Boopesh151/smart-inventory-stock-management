"""Product CRUD HTTP endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.crud import (
    DuplicateSkuError,
    create_product,
    delete_product,
    get_product,
    list_low_stock_products,
    list_products,
    update_product,
)
from backend.database import get_db
from backend.schemas import ProductCreate, ProductListResponse, ProductRead, ProductUpdate

router = APIRouter(prefix="/products", tags=["Products"])

DbSession = Annotated[Session, Depends(get_db)]


def _raise_duplicate_sku(error: DuplicateSkuError) -> None:
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"SKU '{error.sku}' is already used by another product.",
    )


def _get_product_or_404(db: Session, product_id: int):
    product = get_product(db, product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} was not found.",
        )
    return product


@router.post(
    "/",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a product",
)
def create_product_endpoint(payload: ProductCreate, db: DbSession):
    """Add a new product to inventory."""
    try:
        return create_product(db, payload)
    except DuplicateSkuError as error:
        _raise_duplicate_sku(error)


@router.get(
    "/",
    response_model=ProductListResponse,
    summary="List products",
)
def list_products_endpoint(
    db: DbSession,
    skip: int = Query(0, ge=0, description="Number of rows to skip (pagination)."),
    limit: int = Query(10, ge=1, le=100, description="Page size (max 100)."),
    search: str | None = Query(
        None,
        description="Optional filter: matches product name or SKU.",
    ),
):
    """Return a paginated list. Use `search` to filter by name or SKU."""
    items, total = list_products(db, skip=skip, limit=limit, search=search)
    return ProductListResponse(total=total, skip=skip, limit=limit, items=items)


@router.get(
    "/low-stock",
    response_model=list[ProductRead],
    summary="List low-stock products",
)
def list_low_stock_products_endpoint(db: DbSession):
    """Return products whose quantity is at or below minimum_stock_level.

    This path is declared before /{product_id} so FastAPI does not treat
    "low-stock" as an integer id.
    """
    return list_low_stock_products(db)


@router.get(
    "/{product_id}",
    response_model=ProductRead,
    summary="Get one product",
)
def get_product_endpoint(product_id: int, db: DbSession):
    """Return a single product by id."""
    return _get_product_or_404(db, product_id)


@router.put(
    "/{product_id}",
    response_model=ProductRead,
    summary="Update a product",
)
def update_product_endpoint(
    product_id: int,
    payload: ProductUpdate,
    db: DbSession,
):
    """Replace all fields of an existing product."""
    product = _get_product_or_404(db, product_id)
    try:
        return update_product(db, product, payload)
    except DuplicateSkuError as error:
        _raise_duplicate_sku(error)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product",
)
def delete_product_endpoint(product_id: int, db: DbSession):
    """Delete a product. Returns no body when successful."""
    product = _get_product_or_404(db, product_id)
    delete_product(db, product)
    return None
