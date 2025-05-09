import asyncio
import json
from typing import Literal, Self

import websockets
from websockets.asyncio.client import ClientConnection as WebSocket
from websockets.exceptions import ConnectionClosedError

from mmisp.worker.controller.connection_manager import ConnectionManager
from mmisp.worker.node.config import node_config


class ClientConnectionManager(ConnectionManager):
    def __init__(self: Self) -> None:
        super().__init__()
        self.connection: WebSocket | None = None

    async def try_connect(self: Self) -> None:
        header = {"Authorization": f"Bearer {node_config.worker_api_key}"}
        for i in range(1, 100):
            try:
                async with websockets.connect(str(node_config.worker_api_url), additional_headers=header) as websocket:
                    await websocket.close()
                    break
            except OSError:
                print(f"Connection try {i}/100 failed, retrying again...")
                await asyncio.sleep(5)

    async def connect(self: Self) -> None:
        header = {"Authorization": f"Bearer {node_config.worker_api_key}"}
        while True:
            try:
                async with websockets.connect(str(node_config.worker_api_url), additional_headers=header) as websocket:
                    self.connection = websocket
                    print("Connected to master.")
                    while True:
                        message = await websocket.recv()
                        command = json.loads(message)
                        self.receive_msg(command)
            except ConnectionClosedError as e:
                print(e)
                print("Connection Lost. Reconnect in 5 seconds")
                await asyncio.sleep(5)

    async def disconnect(self: Self) -> None:
        if self.connection is not None:
            await self.connection.close()
            self.connection = None

    async def send_json(self: Self, ws: WebSocket, payload: dict) -> None:  # type: ignore[override]
        await ws.send(json.dumps(payload))

    async def send_msg_and_wait(  # type: ignore[override]
        self: Self, command: str | dict | list, conversation_id: str | None = None, timeout: int = 10
    ) -> dict | Literal["Timeout"]:
        ws = self.connection
        return await super().send_msg_and_wait(ws, command, conversation_id, timeout=timeout)

    async def send_msg_nowait(self: Self, command: str | dict | list, conversation_id: str | None = None) -> None:  # type: ignore[override]
        ws = self.connection
        await super().send_msg_nowait(ws, command, conversation_id)
