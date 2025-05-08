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


@pytest_asyncio.fixture
async def websocket_server():
    async with AsyncClient(transport=ASGIWebSocketTransport(app), base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def websocket_client(websocket_server):
    async with aconnect_ws("https://testserver/worker/ws", websocket_server, headers=headers) as ws:
        yield ws


@pytest.mark.asyncio
async def test_app(websocket_client) -> None:
    assert len(connection_manager.active_connections) > 0


@pytest.mark.asyncio
async def test_wrong_auth(websocket_server):
    with pytest.raises(Exception):
        async with aconnect_ws("https://testserver/worker/ws", websocket_server, headers=wrong_headers) as ws:
            assert not ws
