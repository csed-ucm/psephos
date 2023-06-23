# Handle WebSocket connections
from typing import Annotated
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from app.models.documents import Account
from app.websocket_manager import WebSocketManager
from app.dependencies import websocket_auth
from app.account_manager import AccessToken


router = APIRouter()

# Create a connection manager to manage WebSocket connections
manager = WebSocketManager()


@router.websocket("")
async def open_websocket_endpoint(websocket: WebSocket, auth: Annotated[str, Depends(websocket_auth)]):
    await manager.connect(websocket)
    print("auth: ", auth)
    if auth["cookie"]:
        print("cookie: ", auth.cookie)
        # account_id = AccessToken.find(user_id=auth.token)
    elif auth["token"]:
        print("token: ", auth.token)
    else:
        print("no auth")
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
