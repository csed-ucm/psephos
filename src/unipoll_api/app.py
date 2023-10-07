import json
import uvicorn
import os
import argparse
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
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name

    await init_beanie(
        database=mainDB,  # type: ignore
        document_models=documentModels  # type: ignore
    )


# Run the application
def start_server(host: str = settings.host, port: int = settings.port, reload: bool = settings.reload):
    uvicorn.run('unipoll_api.app:app', reload=reload, host=host, port=port)


# Check if IP address is valid
def check_ip(arg_value):
    address = arg_value.split(".")
    if len(address) != 4:
        raise argparse.ArgumentTypeError("invalid host value")
    for i in address:
        if int(i) > 255 or int(i) < 0:
            raise argparse.ArgumentTypeError("invalid host value")
    return arg_value


def cli_entry_point():
    args = cli_args.parse_args()

    if args.command == "run":
        run(args.host, args.port, args.reload)
    elif args.command == "setup":
        setup()
    elif args.command == "get-openapi":
        get_openapi()
    else:
        print("Invalid command")


def run(host=settings.host, port=settings.port, reload=settings.reload):
    # args = run_parser.parse_args()
    colored_dbg.info("University Polling API v{}".format(version))
    start_server(host, port, reload)


def setup():
    # Print current directory
    # print("Current directory: {}".format(os.getcwd()))

    # Get user input
    host = input("Host IP address [{}]: ".format(settings.host))
    port = input("Host port number [{}]: ".format(settings.port))
    mongodb_url = input("MongoDB URL [{}]: ".format(settings.mongodb_url))
    origins = input("Origins [{}]: ".format(settings.origins))
    admin_email = input("Admin email [{}]: ".format(settings.admin_email))

    # Write to .env file
    with open(".env", "w") as f:
        f.write("HOST={}\n".format(host if host else settings.host))
        f.write("PORT={}\n".format(port if port else settings.port))
        f.write("MONGODB_URL={}\n".format(mongodb_url if mongodb_url else settings.mongodb_url))
        f.write("ORIGINS={}\n".format(origins if origins else settings.origins))
        f.write("ADMIN_EMAIL={}\n".format(admin_email if admin_email else settings.admin_email))

    # Print success message
    print(f"Your configuration has been saved to {os.getcwd()}/.env")


def get_openapi():
    if not app.openapi_schema:
        openapi_schema = app.openapi()
        app.openapi_schema = openapi_schema
    json.dump(app.openapi_schema, open("openapi.json", "w"), indent=2)

    # Print success message
    print(f"OpenAPI schema saved to {os.getcwd()}/openapi.json")
