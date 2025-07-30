from fastapi import status
from unipoll_api.exceptions.resource import APIException


class AuthenticationError(APIException):
    def __init__(self):
        super().__init__(code=status.WS_1008_POLICY_VIOLATION,
                         detail="Invalid access token or authorization header")


class InvalidAction(APIException):
    def __init__(self, action: str):
        super().__init__(code=status.WS_1003_UNSUPPORTED_DATA,
                         detail=f'Action "{action}" not found')


class InvalidMessageData(APIException):
    def __init__(self, action: str, valid_args: list[str], data: list[str]):
        super().__init__(code=status.WS_1003_UNSUPPORTED_DATA,
                         detail=f'Invalid data for action "{action}".' +
                                f'Valid arguments are: {valid_args}.' +
                                f'You provided: {data}')


class ActionMissingRequiredArgs(APIException):
    def __init__(self, action: str, required_args: list[str], provided_args: list[str]):
        super().__init__(code=status.WS_1003_UNSUPPORTED_DATA,
                         detail=f"The action '{action}' requires arguments: {required_args}. " +
                                f"You provided: {provided_args}")
