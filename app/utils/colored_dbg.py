from colorama import Fore


# Print message with green INFO header(default)
def print_in_color(*message, color, type, source=""):
    message = ' '.join([str(i) for i in message])
    print("{color}{type}{source}{message}".format(
        type    = type + Fore.RESET + ":" + (9-len(type))*" ",
        color   = color,
        source  = source, 
        message = message))

def info(*message):
    print_in_color(*message, color=Fore.GREEN, type="INFO")

# Print message with red ERROR header
# Used for critical errors
def print_error(*message):
    print_in_color(*message, color=Fore.RED, type="ERROR")

# Print message with yellolw ERROR header
# Used for non-critical errors that won't affect app performance
def print_warning(*message):
    print_in_color(*message, color=Fore.YELLOW, type="WARNING")

# Print message with blue MESSAGE header
# Used for displaying sent/recieved WS messages to/from clients/sweepapi
def print_message(*message, source="SWEEP"):
    print_in_color(*message, color=Fore.BLUE, type="MESSAGE", source=f"from {source}: ")