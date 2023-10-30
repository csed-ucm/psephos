from fastapi import APIRouter
from unipoll_api.utils import api_versioning
from .v1 import router as v1_router
from .v2 import router as v2_router
from .swagger_docs import create_doc_router
from .websocket import router as websocket_router


# Function to create API Router
def create_router(app, default_version):
    # API Router that contains all of the endpoints
    router = APIRouter()

    # Dictionary of endpoints for each version of the API
    endpoints = {
        1: v1_router,
        2: v2_router,
    }

    # Default API version
    router.include_router(endpoints[default_version])
    router.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])

    # API v1
    router.include_router(v1_router, prefix="/v1")  # Add API v1 endpoints to the app
    api_versioning.add_api(v1_router, version=1)    # Add API v1 OpenAPI schemas

    # API v2
    router.include_router(v2_router, prefix="/v2")  # Add API v2 endpoints to the app
    api_versioning.add_api(v2_router, version=2)    # Add API v2 OpenAPI schemas

    # Swagger Documentation Endpoints
    router.include_router(create_doc_router(app, default_version))

    return router
