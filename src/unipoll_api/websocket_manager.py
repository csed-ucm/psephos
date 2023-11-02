from fastapi import WebSocket
from typing import Any
import inspect
from pydantic import BaseModel
from unipoll_api.schemas.websocket import Message
from unipoll_api import actions
from unipoll_api.exceptions import websocket as WebSocketExceptions


class WebSocketManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket) -> None:
        await websocket.send_json(message)

    async def broadcast(self, message: str) -> None:
        for connection in self.active_connections:
            await connection.send_json(message)


def filter_arguments(action, data):
    sig = inspect.signature(action)
    required_args = []
    for param in sig.parameters.values():
        if param.kind == param.POSITIONAL_OR_KEYWORD and param.default == param.empty: 
            required_args.append(param.name)

    filtered_args = {}
    for key in required_args:
        value = data.get(key)
        if not value:
            raise WebSocketExceptions.ActionMissingRequiredArgs(action.__name__, required_args, list(data.keys()))
        filtered_args[key] = value
    return filtered_args


functions = {name: func for name, func in inspect.getmembers(actions, inspect.isfunction)}


async def action_parser(message: Message) -> BaseModel:
    action = functions.get(message.action)
    if not action:
        raise WebSocketExceptions.InvalidAction(message.action)
    args = filter_arguments(action, message.data)
    response: BaseModel = await action(**args)
    return response.model_dump(exclude_none=True)
