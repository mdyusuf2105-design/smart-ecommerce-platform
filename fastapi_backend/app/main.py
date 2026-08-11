from fastapi import FastAPI

from app.database.database import Base, engine
from app.models.user import User
from app.models.product import Product
from app.models.cart import Cart
from app.routers.auth import router as auth_router
from app.routers.product import router as product_router
from app.routers.cart import router as cart_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Smart E-Commerce API",
    description="Backend API for Smart E-Commerce Platform",
    version="1.0.0"
)


app.include_router(auth_router)
app.include_router(product_router)
app.include_router(cart_router)


@app.get("/")
def root():
    return {
        "message": "Smart E-Commerce API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }