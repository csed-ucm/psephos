from datetime import datetime
import json
import uvicorn
import os
import argparse
from fastapi import FastAPI, APIRouter
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from beanie import init_beanie
# from unipoll_api.routes import router, websocket
from unipoll_api.routes import create_router, v1_router, v2_router
from unipoll_api.mongo_db import mainDB, documentModels
from unipoll_api.config import get_settings


# Application start time
start_time = datetime.now()

# Apply setting from configuration file
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    docs_url=None,                         # Disable default docs
    redoc_url=None,                        # Disable default redoc
    title=settings.app_name,               # Title of the application
    description=settings.app_description,  # Description of the application
    version=settings.app_version,          # Version of the application
)


# Add endpoints defined in the routes directory
app.include_router(create_router(app, 2))  # Set default API version to 2

# Add CORS middleware to allow cross-origin requests
origins = settings.origins.split(",")

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
    # for route in app.routes:
    #     if isinstance(route, APIRoute):
    #         route.operation_id = route.name

    await init_beanie(
        database=mainDB,  # type: ignore
        document_models=documentModels  # type: ignore
    )