
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Product

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_products = db.query(func.count(Product.id)).scalar() or 0

    total_units = (
        db.query(func.coalesce(func.sum(Product.quantity), 0)).scalar() or 0
    )

    low_stock_count = (
        db.query(func.count(Product.id))
        .filter(Product.quantity <= Product.minimum_stock_level)
        .scalar() or 0
    )

    inventory_value = (
        db.query(
            func.coalesce(
                func.sum(Product.quantity * Product.price), 0
            )
        ).scalar() or Decimal("0")
    )

    return {
        "total_products": total_products,
        "total_units": total_units,
        "low_stock_count": low_stock_count,
        "inventory_value": str(inventory_value),
    }