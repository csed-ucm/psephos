# Handle WebSocket connections
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, WebSocketException, HTTPException
from unipoll_api.websocket_manager import WebSocketManager, action_parser
from unipoll_api.dependencies import websocket_auth, set_active_user
from unipoll_api.documents import Account
from unipoll_api.schemas.websocket import Message
from unipoll_api.utils import Debug
from unipoll_api.exceptions.resource import APIException
from unipoll_api.exceptions import websocket as WebSocketExceptions


router: APIRouter = APIRouter()

# Create a connection manager to manage WebSocket connections
manager = WebSocketManager()


@router.websocket("")
async def open_websocket_endpoint(websocket: WebSocket, user: Account = Depends(websocket_auth)):
    # Connect to the WebSocket
    await manager.connect(websocket)

    # Check if user is authenticated
    if not user:
        error = WebSocketExceptions.AuthenticationError()
        raise WebSocketException(error.code, error.detail)

    # Set the active user
    await set_active_user(user)

    # Send a welcome message and log the connection
    Debug.info(f"{user.email} connected via websocket")
    await manager.send_personal_message(f"Welcome, {(user.first_name).capitalize()}", websocket)

    # Wait for incoming messages
    try:
        while True:
            try:
                # Receive a message from the client and parse it
                data = await websocket.receive_json()
                message = Message(action=data["action"], data=data.get("data"))
                # Respond to the client with the result of the action
                await manager.send_personal_message(await action_parser(message), websocket)
            # Catch API exceptions and send them to the client
            except (APIException, HTTPException) as e:
                await manager.send_personal_message({'error': e.detail}, websocket)
    # Disconnect the client when the connection is closed
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
