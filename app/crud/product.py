from sqlalchemy import select, func
from sqlalchemy.orm import joinedload, Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class CRUDProduct:
    def _get_joinedload_attrs_option(self):
        return (
            joinedload(Product.cpu_attributes),
            joinedload(Product.cpu_cooler_attributes),
            joinedload(Product.case_attributes),
            joinedload(Product.gpu_attributes),
            joinedload(Product.motherboard_attributes),
            joinedload(Product.power_supply_attributes),
            joinedload(Product.ram_attributes),
            joinedload(Product.storage_attributes),
        )

    def create(self, db: Session, *, obj_in: ProductCreate) -> Product:
        db_obj = Product(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj, attribute_names=["category"])
        return db_obj

    def get(self, db: Session, id_: int):
        return db.get(Product, id_, options=(self._get_joinedload_attrs_option()))

    def get_multi(self, db: Session, *, page: int = 1, page_size: int = 20):
        stmt = (
            select(Product)
            .options(
                *self._get_joinedload_attrs_option()
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        total = db.scalar(select(func.count()).select_from(Product))
        return db.scalars(stmt).all(), total

    def update(self, db: Session, *, db_obj: Product, obj_in: ProductUpdate):
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id_: int):
        obj = db.get(Product, id_)
        if obj:
            db.delete(obj)
            db.commit()

    def get_random_per_category(self, db: Session) -> list[Product]:
            subq = (
                select(
                    Product.id.label("id"),
                    func.row_number()
                    .over(
                        partition_by=Product.category_id,
                        order_by=func.random(),
                    )
                    .label("rn"),
                )
                .where(Product.category_id.isnot(None))
                .subquery()
            )

            result = (
                db.query(Product)
                .options(joinedload(Product.category))
                .join(subq, Product.id == subq.c.id)
                .filter(subq.c.rn == 1)
                .all()
            )
            return result

product_crud = CRUDProduct()
