from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.product import ProductRead, ProductUpdate
from app.crud.product import product_crud
from app.services.keepa import fetch_product_from_keepa

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/{asin}", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def add_product(asin: str, db: Session = Depends(get_db)):
    obj_in = fetch_product_from_keepa(asin, db=db)
    return product_crud.create(db, obj_in=obj_in)

@router.get("/", response_model=list[ProductRead])
def list_products(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    items, _ = product_crud.get_multi(db, page=page, page_size=page_size)
    return items

@router.get(
    "/random-per-category",
    response_model=list[ProductRead],
    summary="One random product from each category",
)
def random_product_per_category(db: Session = Depends(get_db)):
    items = product_crud.get_random_per_category(db=db)
    if not items:
        raise HTTPException(status_code=404, detail="No products found")
    return items

@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    obj = product_crud.get(db, product_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj

@router.put("/{product_id}", response_model=ProductRead)
def update_product(product_id: int, item: ProductUpdate, db: Session = Depends(get_db)):
    obj = product_crud.get(db, product_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return product_crud.update(db, db_obj=obj, obj_in=item)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product_crud.remove(db, id_=product_id)
