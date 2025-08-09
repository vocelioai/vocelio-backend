# apps/billing-pro/src/api/v1/api.py
from fastapi import APIRouter
from api.v1.endpoints import billing, subscriptions, invoices, payments, analytics

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(billing.router, prefix="/billing", tags=["Billing"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["Invoices"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
