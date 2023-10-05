import argparse
import textwrap
from unipoll_api.config import get_settings

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


# Parse CLI arguments
def parse_args():
    parser = argparse.ArgumentParser(description="University Polling API")
    subparser = parser.add_subparsers(title='Available commands', dest='command', required=True)

    run_parser = subparser.add_parser('run',
                                      help="Run the API server",
                                      formatter_class=argparse.RawDescriptionHelpFormatter,
                                      description=textwrap.dedent('''\
        Run University Polling API
        --------------------------------
        Examples:

            python main.py --reload --host=127.0.0.1 --port=8000
            python main.py --reload
        '''))

    run_parser.add_argument("--reload", action="store_true", help="Enable auto-reload", default=False)
    run_parser.add_argument("--host", type=check_ip, default=settings.host, help="Host IP address")
    run_parser.add_argument("--port", type=int, default=settings.port, help="Host port number")

    subparser.add_parser('setup', help="Setup the API server")
    subparser.add_parser('get-openapi', help="Get the OpenAPI schema")

    return parser.parse_args()
