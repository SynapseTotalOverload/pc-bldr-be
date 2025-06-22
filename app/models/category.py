from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.orm import relationship
from app.db.base import Base


class Category(Base):
    id = Column(BigInteger, primary_key=True, index=True)
    keepa_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String, nullable=False)

    products = relationship("Product", back_populates="category")

    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)