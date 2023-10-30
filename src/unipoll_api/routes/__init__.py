from fastapi import APIRouter
from fastapi.routing import APIRoute
from unipoll_api.utils import api_versioning
from .v1 import router as v1_router
from .v2 import router as v2_router
from .swagger_docs import create_doc_router
from .websocket import router as websocket_router


# TODO: find a way to generate unique IDs for different versions with one function

# Function to generate unique IDs for API v1 endpoints
def generate_unique_id_v1(route: APIRoute):
    return f"api-v1-{route.tags[0]}-{route.name}"


# Function to generate unique IDs for API v2 endpoints
def generate_unique_id_v2(route: APIRoute):
    return f"api-v2-{route.tags[0]}-{route.name}"


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

    # Add API v1 endpoints to the main router
    router.include_router(v1_router,
                          prefix="/v1",
                          generate_unique_id_function=generate_unique_id_v1)
    # Add API v1 OpenAPI schemas for documentation
    api_versioning.add_api(v1_router, version=1)

    # Add API v2 endpoints to the main router
    router.include_router(v2_router,
                          prefix="/v2",
                          generate_unique_id_function=generate_unique_id_v2)
    # Add API v2 OpenAPI schemas for documentation
    api_versioning.add_api(v2_router, version=2)

    # Swagger Documentation Endpoints
    router.include_router(create_doc_router(app, default_version))

    # Return the main router
    return router
