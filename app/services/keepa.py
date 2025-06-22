from __future__ import annotations

from decimal import Decimal
from math import isfinite
from typing import Any, Union, Sequence
import zlib

import keepa
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.category import Category
from app.schemas.product import ProductCreate

settings = get_settings()
api = keepa.Keepa(settings.keepa_key)
api.category_lookup
api.search_for_categories
api.product_finder
keepa.ProductParams

def _last_valid(seq: Sequence[Union[int, float, None]]) -> Union[int, float, None]:
    return next((v for v in reversed(seq) if v not in (None, -1)), None)


def _price_to_float(raw: Union[int, float, None]) -> float | None:
    if raw in (None, -1):
        return None
    if isinstance(raw, int):
        raw = float(Decimal(raw) / 100)
    return float(raw) if isfinite(raw) else None


def _safe_float(v: Union[int, float, None]) -> float | None:
    return round(float(v), 2) if v is not None and isfinite(float(v)) else None


def ensure_category(p: dict[str, Any], db: Session) -> int | None:
    # 1) Real Keepa catId, if > 0
    cat_ids = (
        p.get("categories")
        or ([p["category"]] if p.get("category") else None)
        or ([p["rootCategory"]] if p.get("rootCategory") else None)
    )
    if cat_ids and (cat_id := cat_ids[0]) and cat_id > 0:
        stmt = select(Category).where(Category.keepa_id == cat_id)
        cat = db.execute(stmt).scalar_one_or_none()
        if cat is None:
            name = (p.get("categoryTree", [{}])[-1].get("name") or f"Keepa #{cat_id}")
            cat = Category(keepa_id=cat_id, name=name)  # type: ignore[arg-type]
            db.add(cat); db.commit(); db.refresh(cat)
        return cat.id

    virt_name = p.get("productGroup") or p.get("productTypeName") or "Miscellaneous"
    virt_keepa_id = -zlib.crc32(virt_name.encode())   # deterministic negative id

    stmt = select(Category).where(Category.keepa_id == virt_keepa_id)
    cat = db.execute(stmt).scalar_one_or_none()
    if cat is None:
        cat = Category(keepa_id=virt_keepa_id, name=virt_name)  # type: ignore[arg-type]
        db.add(cat); db.commit(); db.refresh(cat)
    return cat.id


def fetch_product_from_keepa(asin: str, db: Session, domain: str = "US") -> ProductCreate:
    products = api.query(
        asin,
        domain=domain,
        history=True,
        rating=True,
        stats=90,
    )
    with open('product.json', 'w') as f:
        f.write(str(products))
    api.search_for_categories
    if not products:
        raise ValueError(f"ASIN {asin} not found on Keepa")

    p = products[0]
    data = p.get("data", {})

    price = _price_to_float(
        _last_valid(data.get("AMAZON", []))
        or _last_valid(data.get("NEW", []))
        or _last_valid(data.get("USED", []))
    )

    stats = p.get("stats") or {}
    rating_raw = stats.get("avgRating") or p.get("rating")
    if rating_raw is None and "RATING" in data:
        rating_raw = (_last_valid(data["RATING"]) or 0)
    rating = _safe_float(rating_raw)

    category_id = ensure_category(p, db)

    return ProductCreate(
        asin=asin,
        title=p.get("title") or "",
        price=price,
        rating=rating,
        category_id=category_id,
    )
