from fastapi import APIRouter
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from unipoll_api.utils import api_versioning


# Function to create router for documentation endpoints
def create_doc_router(app, default_version):
    # Router for documentation endpoints
    doc_router = APIRouter()

    @doc_router.get("/v{version}/openapi.json", include_in_schema=False)
    async def get_openapi_schema(version: int):
        return api_versioning.openapi_schemas[version]

    # Default Docs
    @doc_router.get("/docs", include_in_schema=False)
    async def default_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=f"/v{default_version}/openapi.json",
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
        )

    # Versioned Docs
    @doc_router.get("/v{version}/docs", include_in_schema=False)
    async def versioned_swagger_ui_html(version: int):
        return get_swagger_ui_html(
            openapi_url=f"/v{version}/openapi.json",
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
        )

    @doc_router.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()

    @doc_router.get("/redoc", include_in_schema=False)
    async def redoc_html():
        return get_redoc_html(
            openapi_url="/openapi.json",
            title=app.title + " - ReDoc",
            redoc_js_url="https://unpkg.com/redoc@next/bundles/redoc.standalone.js",
        )

    return doc_router
