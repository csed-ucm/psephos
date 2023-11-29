import json
import uvicorn
import os
import argparse

from fastapi import APIRouter
from fastapi.openapi import utils as OpenAPIUtils


from unipoll_api.config import get_settings
from unipoll_api.__version__ import version
from unipoll_api.utils import cli_args, colored_dbg
# from unipoll_api.plugins import init_plugins
# from unipoll_api.plugin_manager import PluginManager


# Apply setting from configuration file
settings = get_settings()


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
        get_openapi(args.version)
    else:
        print("Invalid command")


def run(host=settings.host, port=settings.port, reload=settings.reload):  
    colored_dbg.info("University Polling API v{}".format(version))
    uvicorn.run('unipoll_api.app:app', reload=reload, host=host, port=port)


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

# TODO: Get version list dynamically
def get_openapi(versions: list[int] = [1, 2]):
    from unipoll_api.app import app
    if not app.openapi_schema:
        from unipoll_api.routes import generate_unique_id, API_VERSIONS

        router = APIRouter()
        for i in versions:
            router.include_router(API_VERSIONS[f'v{i}'],
                                  prefix=f"/v{i}",
                                  generate_unique_id_function=generate_unique_id(i))
        

        openapi_schemas = OpenAPIUtils.get_openapi(title=app.title,
                                                   version=settings.app_version,
                                                   routes=router.routes)
        openapi_schema = openapi_schemas
        app.openapi_schema = openapi_schema
    json.dump(app.openapi_schema, open("openapi.json", "w"), indent=2)

    # Print success message
    print(f"OpenAPI schema saved to {os.getcwd()}/openapi.json")
