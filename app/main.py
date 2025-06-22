from fastapi import FastAPI
from app.core.config import get_settings
from app.api.v1 import router as products_router

settings = get_settings()
app = FastAPI(title=settings.app_name)
app.include_router(products_router, prefix=settings.api_prefix)
