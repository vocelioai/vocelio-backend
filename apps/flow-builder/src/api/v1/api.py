# apps/flow-builder/src/api/v1/api.py
from fastapi import APIRouter
from .endpoints import flows, nodes, templates, execution

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(flows.router, prefix="/flows", tags=["flows"])
api_router.include_router(nodes.router, prefix="/nodes", tags=["nodes"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(execution.router, prefix="/execution", tags=["execution"])

@api_router.get("/")
async def api_root():
    """API root endpoint"""
    return {
        "message": "Flow Builder API v1",
        "endpoints": {
            "flows": "/flows",
            "nodes": "/nodes", 
            "templates": "/templates",
            "execution": "/execution"
        }
    }