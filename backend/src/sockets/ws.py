from fastapi import WebSocket, WebSocketDisconnect, status
from services.user_service import UserService
import json


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        print(f"Usuário {user_id} conectado. Total: {len(self.active_connections[user_id])} conexões")

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        print(f"Usuário {user_id} desconectado")

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    print(f"Erro ao enviar mensagem: {e}")

    async def broadcast_from_user(self, message: str, user_id: int, nome: str):
        payload = {
            "user_id": user_id,
            "nome": nome,
            "mensagem": message
        }
        await self.broadcast(json.dumps(payload))

    def get_active_users(self) -> list[int]:
        return list(self.active_connections.keys())


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, token: str | None = None):
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Token não fornecido")
        return

    payload = UserService.verify_token(token)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Token inválido ou expirado")
        return

    user_id = payload.get("user_id")
    email = payload.get("email")
    
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Usuário {user_id} ({email}): {data}")
            await manager.broadcast_from_user(data, user_id, email.split("@")[0])

    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
    except Exception as e:
        print(f"Erro no WebSocket: {e}")
        manager.disconnect(user_id, websocket)