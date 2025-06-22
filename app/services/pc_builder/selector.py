from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Product, 
    BaseAttrsModel,
    CPUAttributes,
    CPUCoolerAttributes,
    GPUAttributes,
    MotherboardAttributes,
    RAMAttributes,
    StorageAttributes,
    PowerSupplyAttributes,
    CaseAttributes,
)
from app.services.pc_builder.enums import COMPONENTS_ENUM
from app.services.pc_builder.rules import RuleBase


class ComponentSelector:
    """
    Selects the best component of a specific type based on rules and budget.
    """
    component_types_to_attr_model_mapping: dict[str,type[BaseAttrsModel]] = {
        "cpu": CPUAttributes,
        "cpu_cooler": CPUCoolerAttributes,
        "gpu": GPUAttributes,
        "motherboard": MotherboardAttributes,
        "ram": RAMAttributes,
        "storage": StorageAttributes,
        "psu": PowerSupplyAttributes,
        "case": CaseAttributes,
    }

    def __init__(
        self,
        budget: float,
        rules: list[RuleBase],
        session: Session,
        component_type: Optional[str] = None,
    ):
        self.budget = budget
        self.rules = rules
        self.session = session
        self.component_type = component_type

    @property
    def component_type(self) -> str:
        return self._component_type

    @component_type.setter
    def component_type(self, component_type: str) -> None:
        if component_type in COMPONENTS_ENUM or component_type is None:
            self._component_type = component_type
        else:
            raise Exception("Incorrect component type for component selector")

    def select_best(self) -> Optional[Product]:
        """
        Selects the best product based on rules.
        """
        if not self.component_type:
            raise Exception("Component type is not set")

        # STEP 1: Get all products for this type
        products = self._fetch_all_products()

        # STEP 2: Filter by rules
        for rule in self.rules:
            products = rule.apply(products, self.component_type)

        # STEP 3: Sort by price/performance or custom logic
        products = sorted(products, key=lambda p: p.updated_at)

        return products[0] if products else None

    def _fetch_all_products(self) -> list[Product]:
        """
        Fetch products by component type (e.g., only CPUs if component_type = 'cpu').
        """
        AttrsModel = self.component_types_to_attr_model_mapping[self.component_type]
        result = self.session.execute(select(Product).join(AttrsModel))
        return result.scalars().all()
