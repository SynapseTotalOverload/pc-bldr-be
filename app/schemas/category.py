from datetime import datetime
from pydantic import BaseModel


class CategoryBase(BaseModel):
    keepa_id: int
    name: str


class CategoryCreate(CategoryBase):
    pass

class CategoryRead(BaseModel):
    id: int
    keepa_id: int
    name: str

    class Config:
        from_attributes = True