# apps/developer-api/src/api/v1/api.py
from fastapi import APIRouter
from api.v1.endpoints import keys, webhooks, sdk, documentation, testing

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(keys.router, prefix="/keys", tags=["API Keys"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
api_router.include_router(sdk.router, prefix="/sdk", tags=["SDK"])
api_router.include_router(documentation.router, prefix="/docs", tags=["Documentation"])
api_router.include_router(testing.router, prefix="/test", tags=["Testing"])
