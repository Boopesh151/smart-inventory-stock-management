"""Database operations for products.

The router talks to these functions instead of writing SQLAlchemy
queries inline. That keeps route handlers short and easier to read.
"""

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.models import Product, StockTransaction, utc_now
from backend.schemas import ProductCreate, ProductUpdate, StockTransactionCreate

class DuplicateSkuError(Exception):
    """Raised when another product already uses the same SKU."""

    def __init__(self, sku: str):
        self.sku = sku
        super().__init__(f"SKU '{sku}' is already in use")


def _escape_like_pattern(text: str) -> str:
    """Escape %, _, and \\ so search text is treated as plain text."""
    return (
        text.replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )


def get_product(db: Session, product_id: int) -> Product | None:
    """Return one product by id, or None if it does not exist."""
    return db.get(Product, product_id)


def get_product_by_sku(db: Session, sku: str, exclude_id: int | None = None) -> Product | None:
    """Find a product with this SKU. Used to enforce uniqueness."""
    query = db.query(Product).filter(Product.sku == sku)
    if exclude_id is not None:
        query = query.filter(Product.id != exclude_id)
    return query.first()


def list_products(
    db: Session,
    skip: int,
    limit: int,
    search: str | None = None,
) -> tuple[list[Product], int]:
    """Return a page of products and the total matching count."""
    query = db.query(Product)

    if search:
        pattern = f"%{_escape_like_pattern(search.strip())}%"
        query = query.filter(
            or_(
                Product.name.ilike(pattern, escape="\\"),
                Product.sku.ilike(pattern, escape="\\"),
            )
        )

    total = query.count()
    items = (
        query.order_by(Product.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return items, total


def list_low_stock_products(db: Session) -> list[Product]:
    """Return products at or below their minimum stock level."""
    return (
        db.query(Product)
        .filter(Product.quantity <= Product.minimum_stock_level)
        .order_by(Product.id)
        .all()
    )


def create_product(db: Session, data: ProductCreate) -> Product:
    """Insert a new product. Raises DuplicateSkuError if the SKU exists."""
    if get_product_by_sku(db, data.sku) is not None:
        raise DuplicateSkuError(data.sku)

    product = Product(
        name=data.name,
        sku=data.sku,
        category=data.category,
        quantity=data.quantity,
        price=data.price,
        supplier=data.supplier,
        minimum_stock_level=data.minimum_stock_level,
    )
    db.add(product)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateSkuError(data.sku)
    db.refresh(product)
    return product


def update_product(db: Session, product: Product, data: ProductUpdate) -> Product:
    """Replace all editable fields on an existing product."""
    if get_product_by_sku(db, data.sku, exclude_id=product.id) is not None:
        raise DuplicateSkuError(data.sku)

    product.name = data.name
    product.sku = data.sku
    product.category = data.category
    product.quantity = data.quantity
    product.price = data.price
    product.supplier = data.supplier
    product.minimum_stock_level = data.minimum_stock_level
    product.updated_at = utc_now()

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateSkuError(data.sku)
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product) -> None:
    """Remove a product from the database."""
    db.delete(product)
    db.commit()
def create_stock_transaction(
    db: Session,
    data: StockTransactionCreate,
) -> StockTransaction:
    """Add or remove stock and record the transaction."""

    product = get_product(db, data.product_id)

    if product is None:
        raise ValueError(f"Product with id {data.product_id} was not found.")

    if data.transaction_type == "OUT":
        if data.quantity > product.quantity:
            raise ValueError(
                f"Not enough stock. Available quantity: {product.quantity}."
            )

        product.quantity -= data.quantity

    else:
        product.quantity += data.quantity

    product.updated_at = utc_now()

    transaction = StockTransaction(
        product_id=product.id,
        transaction_type=data.transaction_type,
        quantity=data.quantity,
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


def list_stock_transactions(
    db: Session,
    limit: int = 50,
) -> list[StockTransaction]:
    """Return recent stock transactions."""

    return (
        db.query(StockTransaction)
        .order_by(StockTransaction.created_at.desc())
        .limit(limit)
        .all()
    )
def list_stock_transactions(
    db: Session,
    limit: int = 50,
) -> list[StockTransaction]:
    """Return recent stock transactions."""
    return (
        db.query(StockTransaction)
        .order_by(StockTransaction.created_at.desc())
        .limit(limit)
        .all()
    ) 

    """Add or remove stock and record the transaction."""

    product = get_product(db, data.product_id)

    if product is None:
        raise ValueError(f"Product with id {data.product_id} was not found.")

    if data.transaction_type == "OUT":
        if data.quantity > product.quantity:
            raise ValueError(
                f"Not enough stock. Available quantity: {product.quantity}."
            )

        product.quantity -= data.quantity

    else:  # IN
        product.quantity += data.quantity

    product.updated_at = utc_now()

    transaction = StockTransaction(
        product_id=product.id,
        transaction_type=data.transaction_type,
        quantity=data.quantity,
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


