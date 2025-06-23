from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.product import Product
from app.schemas.attributes import (
    CPUAttributesSchema,
    CPUCoolerAttributesSchema,
    GPUAttributesSchema,
    MotherboardAttributesSchema,
    RAMAttributesSchema,
    StorageAttributesSchema,
    PowerSupplyAttributesSchema,
    CaseAttributesSchema,
)
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
    attrs: Optional[dict] = None

    @classmethod
    def from_orm_with_attrs(cls, obj: Product) -> "ProductRead":
        """
        Construct ProductRead instance with resolved attrs field.
        """

        mapping: list[tuple[str, BaseModel]] = [
            ("cpu_attributes", CPUAttributesSchema),
            ("cpu_cooler_attributes", CPUCoolerAttributesSchema),
            ("gpu_attributes", GPUAttributesSchema),
            ("motherboard_attributes", MotherboardAttributesSchema),
            ("ram_attributes", RAMAttributesSchema),
            ("storage_attributes", StorageAttributesSchema),
            ("power_supply_attributes", PowerSupplyAttributesSchema),
            ("case_attributes", CaseAttributesSchema),
        ]

        for attr_name, schema in mapping:
            attrs_model = getattr(obj, attr_name, None)
            if attrs_model:
                return cls(
                    **obj.__dict__,
                    attrs=schema.model_validate(attrs_model).model_dump()
                )

        return cls(**obj.__dict__, attrs=None)
