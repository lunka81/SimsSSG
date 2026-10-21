from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder

#Websocket setup written by Anders. Pushed by me because Anders has some bugs he doesn't want to commit to this branch.
class ConnectionManager:
    def __init__(self):
        self.connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.connections.discard(websocket)

    async def broadcast(self, data: dict):
        message = jsonable_encoder(data)

        for connection in list(self.connections):
            try:
                await connection.send_json(message)
            except (OSError, RuntimeError):
                self.disconnect(connection)


manager = ConnectionManager()


async def send_to_frontend(data: dict):
    await manager.broadcast(data)