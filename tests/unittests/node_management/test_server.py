import asyncio

import pytest
import pytest_asyncio
from httpx import AsyncClient
from httpx_ws import aconnect_ws
from httpx_ws.transport import ASGIWebSocketTransport

from mmisp.worker.config import system_config_data
from mmisp.worker.controller.worker_controller import connection_manager
from mmisp.worker.main import app

headers = {"Authorization": f"Bearer {system_config_data.worker_api_key}"}
wrong_headers = {"Authorization": f"Bearer {system_config_data.worker_api_key}1"}


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def websocket_server():
    async with (
        ASGIWebSocketTransport(app) as transport,
        AsyncClient(transport=transport, base_url="http://testserver") as client,
    ):
        try:
            yield client
            transport.exit_stack = None
        finally:
            await asyncio.sleep(0)


@pytest.mark.asyncio
async def test_app(websocket_server) -> None:
    async with aconnect_ws("https://testserver/worker/ws", websocket_server, headers=headers) as ws:
        assert ws
        assert len(connection_manager.active_connections) > 0


@pytest.mark.asyncio
async def test_wrong_auth(websocket_server):
    with pytest.raises(Exception):
        async with aconnect_ws("https://testserver/worker/ws", websocket_server, headers=wrong_headers) as ws:
            assert not ws
