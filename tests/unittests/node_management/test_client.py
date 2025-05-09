import asyncio
import json

import pytest
import pytest_asyncio
import websockets

from mmisp.worker.node.worker_main import client

PORT = 8765

# Server handler function
connected_clients = []
messages = []


async def server_handler(websocket):
    print("Websocket connected")
    connected_clients.append(websocket)
    while True:
        messages.append(json.loads(await websocket.recv()))


@pytest_asyncio.fixture
async def websocket_server():
    async with websockets.serve(server_handler, "127.0.0.1", PORT) as server:
        await asyncio.sleep(0.5)
        yield server


@pytest_asyncio.fixture
async def websocket_client(websocket_server):
    asyncio.create_task(client.connect())
    while len(connected_clients) < 1:
        await asyncio.sleep(0.5)
    yield
    await client.disconnect()


@pytest.mark.asyncio
async def test(websocket_client):
    assert len(connected_clients) == 1
    c = connected_clients[0]

    await c.send(json.dumps({"msg": "ping", "conversation_id": "abcdef"}))
    await asyncio.sleep(0.5)
    print(messages)
    m = messages.pop()
    assert m["msg"] == "pong"
    assert m["conversation_id"] == "abcdef"
