"""FastAPI entry point for the Smart Inventory backend."""
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import products
from backend.routers import dashboard
from backend.routers import stock
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.database import Base, engine
import backend.models  # registers Product so create_all() can build the table
from backend.routers import products


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run setup when the API starts, then shut down cleanly.

    create_all() looks at every model attached to Base and creates
    missing tables in SQLite. It does not delete existing data.
    """
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Smart Inventory & Stock Management System",
    description="College placement project backend API",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(dashboard.router)
app.include_router(stock.router)


@app.get("/")
def welcome():
    """Return a short welcome message for the root URL."""
    return {
        "message": "Welcome to the Smart Inventory & Stock Management System API"
    }


@app.get("/health")
def health():
    """Return a simple status so we can check that the API is running."""
    return {
        "status": "ok"
    }
