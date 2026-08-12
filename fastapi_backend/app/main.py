from fastapi import FastAPI

from app.database.database import Base, engine
from app.models.user import User
from app.models.product import Product
from app.models.cart import Cart
from app.models.order import Order
from app.routers.auth import router as auth_router
from app.routers.product import router as product_router
from app.routers.cart import router as cart_router
from app.routers.order import router as order_router
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Smart E-Commerce API",
    description="Backend API for Smart E-Commerce Platform",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(product_router)
app.include_router(cart_router)
app.include_router(order_router)


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