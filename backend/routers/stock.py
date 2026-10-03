"""Stock In / Stock Out API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.crud import create_stock_transaction, list_stock_transactions
from backend.database import get_db
from backend.schemas import StockTransactionCreate, StockTransactionRead

router = APIRouter(prefix="/stock", tags=["Stock"])


DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/transaction",
    response_model=StockTransactionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_stock_transaction_endpoint(
    payload: StockTransactionCreate,
    db: DbSession,
):
    """Perform a Stock In or Stock Out transaction."""

    try:
        return create_stock_transaction(db, payload)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
@router.get(
    "/transactions",
    response_model=list[StockTransactionRead],
    )
def list_stock_transactions_endpoint(
    db: DbSession,
    ):
    """Return recent stock transactions."""
    return list_stock_transactions(db)
