import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from beanie import init_beanie
from unipoll_api.routes import router
from unipoll_api.mongo_db import mainDB, documentModels
from unipoll_api.config import get_settings
from unipoll_api.__version__ import version
from unipoll_api.utils import cli_args, colored_dbg


# Apply setting from configuration file
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,               # Title of the application
    description=settings.app_description,  # Description of the application
    version=settings.app_version,          # Version of the application
)

# Add endpoints defined in the routes directory
app.include_router(router)

# Add CORS middleware to allow cross-origin requests
origins = settings.origins

# Middleware
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
        document_models=documentModels  # type: ignore
    )


# Run the application
def start_server(host: str = settings.host, port: int = settings.port, reload: bool = settings.reload):
    uvicorn.run('unipoll_api.app:app', reload=reload, host=host, port=port)


def run():
    args = cli_args.parse_args()
    colored_dbg.info("University Polling API v{}".format(version))
    start_server(args.host, args.port, args.reload)
