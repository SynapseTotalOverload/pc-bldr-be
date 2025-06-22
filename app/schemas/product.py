from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from .category import CategoryRead


class ProductBase(BaseModel):
    asin: str = Field(..., min_length=10, max_length=12)
    title: str
    price: Optional[float] = None
    rating: Optional[float] = None

    class Config:
        from_attributes = True


class ProductCreate(ProductBase):
    category_id: Optional[int] = None


class ProductUpdate(BaseModel):
    title: Optional[str] = None
    price: Optional[float] = None
    rating: Optional[float] = None
    category_id: Optional[int] = None

    class Config:
        from_attributes = True


class ProductRead(ProductBase):
    id: int
    created_at: datetime
    category: Optional[CategoryRead] = None
