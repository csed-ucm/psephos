# Handle WebSocket connections
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from unipoll_api.websocket_manager import WebSocketManager
from unipoll_api.dependencies import websocket_auth
# from unipoll_api.account_manager import active_user
# from unipoll_api import dependencies as Dependencies
from unipoll_api.documents import Account
router: APIRouter = APIRouter()

# Create a connection manager to manage WebSocket connections
manager = WebSocketManager()


@router.websocket("")
async def open_websocket_endpoint(websocket: WebSocket,
                                  user: Account = Depends(websocket_auth)):
    await manager.connect(websocket)
    await websocket.send_text(f"Hello, {user.first_name}")
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}")
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
