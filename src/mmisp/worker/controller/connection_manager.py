import asyncio
import uuid
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Literal, Self, TypeVar

# from fastapi import WebSocket as ServerWebSocket
# from websockets.asyncio.client import ClientConnection as WebSocket

WS = TypeVar("WS")


class ConnectionManager(ABC):
    def __init__(self: Self) -> None:
        self.pending_commands: Dict[str, asyncio.Future] = {}  # command_id -> future
        self.dispatch: Dict[str, Callable] = {}

    @abstractmethod
    async def send_json(self: Self, ws: WS, payload: dict) -> Any: ...

    async def send_msg_nowait(
        self: Self, ws: WS, command: str | dict | list, conversation_id: str | None = None, **extra
    ) -> None:
        if conversation_id is None:
            conversation_id = str(uuid.uuid4())

        payload = {
            "conversation_id": conversation_id,
            "msg": command,
        }
        payload.update(extra)
        await self.send_json(ws, payload)

    async def send_msg_and_wait(
        self: Self, ws: WS, command: str | dict | list, conversation_id: str | None = None, timeout: int = 10, **extra
    ) -> dict | Literal["Timeout"]:
        if conversation_id is None:
            conversation_id = str(uuid.uuid4())
        future = asyncio.get_event_loop().create_future()
        self.pending_commands[conversation_id] = future

        payload = {
            "conversation_id": conversation_id,
            "msg": command,
        }
        payload.update(extra)

        #        ws = self.active_connections[client_id]
        await self.send_json(ws, payload)

        # Wait for response with timeout (default 10s)
        try:
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            return "Timeout"
        finally:
            self.pending_commands.pop(conversation_id, None)

    def receive_msg(self: Self, data: dict) -> None:
        # command_id: str, response: str):
        if "conversation_id" not in data:
            # need to handle commands from the client
            return
        future = self.pending_commands.get(data["conversation_id"])
        if future:
            future.set_result(data)
        else:
            if data["msg"] in self.dispatch:
                asyncio.create_task(self.dispatch[data["msg"]](data))
            else:
                print("Unknown message", data)
