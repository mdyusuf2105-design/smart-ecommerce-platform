from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    name: str
    category: str | None = None
    description: str | None = None
    price: float
    stock: int = 0
    popularity: int = 0
    images: str | None = None


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ProductUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    description: str | None = None
    price: float | None = None
    stock: int | None = None
    popularity: int | None = None
    images: str | None = None