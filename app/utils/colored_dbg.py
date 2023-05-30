from colorama import Fore
from typing import List


# Print colored messages
def print_in_color(
    *message: List[str] | str,
    color: str,
    type: str,
        source: str = "") -> None:
    str_message = ' '.join([str(i) for i in message])
    print("{color}{type}{source}{message}".format(
        type=type + Fore.RESET + ":" + (9 - len(type)) * " ",
        color=color,
        source=source,
        message=str_message))


# For general information
def info(*message: List[str] | str) -> None:
    print_in_color(*message, color=Fore.GREEN, type="INFO")


# For final result of a test
def test_success(*message: List[str] | str) -> None:
    print_in_color(*message, color=Fore.GREEN, type="SUCCESS")


# For general test information
def test_info(*message: List[str] | str) -> None:
    print_in_color(*message, color=Fore.BLUE, type="TESTING")


# Print message with red ERROR header
# Used for critical errors
def print_error(*message: List[str] | str) -> None:
    print_in_color(*message, color=Fore.RED, type="ERROR")


# Used for non-critical errors that won't affect app performance
def print_warning(*message: List[str] | str) -> None:
    print_in_color(*message, color=Fore.YELLOW, type="WARNING")


# Print message with blue MESSAGE header
def print_message(*message: List[str] | str, source: str = "") -> None:
    print_in_color(
        *message,
        color=Fore.BLUE,
        type="MESSAGE",
        source=f"from {source}: ")
