from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.pc_builder.enums import COMPONENTS_ENUM
from app.services.pc_builder.rules import RuleBase, get_rules_for_purpose
from app.services.pc_builder.selector import ComponentSelector
from app.models import Product


class PCBuilder:
    """
    Main class responsible for building a PC based on budget and usage type.
    """

    def __init__(
        self,
        budget: float,
        purpose: str,
        session: Session,
        admin_overrides: dict | None = None,
    ):
        """
        :param budget: Maximum total cost of the build
        :param purpose: Use-case type, e.g., "gaming", "office", "development"
        :param session: SQLAlchemy Async session
        :param admin_overrides: Optional dict to override default logic (e.g. {"cpu": "intel-i5-123456"})
        """
        self.budget = budget
        self.purpose = purpose
        self.session = session
        self.overrides = admin_overrides or {}
        self.rules: List[RuleBase] = []
        self.selected_components: dict[str, Product] = {}

    def load_rules(self) -> None:
        """
        Load rules dynamically based on the use-case.
        """
        self.rules = get_rules_for_purpose(self.purpose)

    def build(self) -> dict[str, Product]:
        """
        Run PC building logic.
        :return: Dictionary of selected components
        """
        self.load_rules()

        selector = ComponentSelector(
            budget=self.budget,
            rules=self.rules,
            session=self.session,
        )
        for component_type in COMPONENTS_ENUM:
            if component_type in self.overrides:
                product = self._get_product_by_asin(self.overrides[component_type])
            else:
                selector.component_type = component_type
                selector.selected_components = self.selected_components
                product = selector.select_best()

            if not product:
                raise Exception(f"Could not find suitable {component_type}")
            self.selected_components[component_type] = product

        return self.selected_components

    def _get_product_by_asin(self, asin: str) -> Product:
        """
        Fetch a product directly by ASIN (used for manual overrides).
        """
        result = self.session.execute(
            select(Product).where(Product.asin == asin)
        )
        return result.scalar_one_or_none()
