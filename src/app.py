from fastapi import FastAPI, Depends
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from beanie import init_beanie
from src.mongo_db import mainDB, DOCUMENT_MODELS
from src.routes import workspace as WorkspaceRoutes
from src.routes import group as GroupRoutes
from src.routes import account as AccountRoutes
from src.routes import websocket as WebSocketRoutes
from src.routes import authentication as AuthenticationRoutes
from src.config import get_settings
from src.dependencies import set_active_user


# Apply setting from configuration file
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,               # Title of the application
    description=settings.app_description,  # Description of the application
    version=settings.app_version,          # Version of the application
)


# Add endpoints defined in the routes directory
app.include_router(WorkspaceRoutes.open_router,
                   prefix="/workspaces",
                   tags=["Workspaces"],
                   dependencies=[Depends(set_active_user)])
app.include_router(WorkspaceRoutes.router,
                   prefix="/workspaces",
                   tags=["Workspaces"],
                   dependencies=[Depends(set_active_user)])
app.include_router(GroupRoutes.router,
                   prefix="/groups",
                   tags=["Groups"],
                   dependencies=[Depends(set_active_user)])
app.include_router(WebSocketRoutes.router,
                   prefix="/ws",
                   tags=["WebSocket"])
app.include_router(AccountRoutes.router,
                   prefix="/accounts",
                   tags=["Accounts"],
                   dependencies=[Depends(set_active_user)])

app.include_router(AuthenticationRoutes.router,
                   prefix="/auth",
                   tags=["Authentication"])

app.include_router(WebSocketRoutes.router,
                   prefix="/ws",
                   tags=["WebSocket"])


# Add CORS middleware to allow cross-origin requests
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Initialize Mongo Database on startup
@app.on_event("startup")
async def on_startup() -> None:
    # Simplify operation IDs so that generated API clients have simpler function names
    # Each route will have its operation ID set to the method name
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name

    await init_beanie(
        database=mainDB,
        document_models=DOCUMENT_MODELS,
    )
