import argparse
import textwrap
from dataclasses import dataclass


@dataclass
class Arguments:
    host: str
    port: int
    reload: bool


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
def parse_args() -> Arguments:
    # Create arg parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
        Run University Polling API
        --------------------------------
        Examples:

            python main.py --reload --host=127.0.0.1 --port=8000
            python main.py --reload
        '''))

    parser.add_argument("--reload", action="store_true",
                        help="Enable auto-reload")
    parser.add_argument("--host", type=check_ip, default="127.0.0.1", help="Host IP address")
    parser.add_argument("--port", type=int, default=8000, help="Host port number")

    return Arguments(**vars(parser.parse_args()))
