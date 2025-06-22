from app.db.session import SessionLocal
from app.services.pc_builder.builder import PCBuilder


with SessionLocal() as db:
    builder = PCBuilder(
        budget=1200.0,
        purpose="gaming",
        session=db,
        admin_overrides={"cpu": "B07JGCSMJX"},
    )

    components = builder.build()
print(components)