from contextlib import ExitStack

import pytest_asyncio
from fastapi.testclient import TestClient

from mmisp.tests.fixtures import *  # noqa
from mmisp.worker.main import init_app
from mmisp.worker.misp_database.misp_api_config import misp_api_config_data


@pytest_asyncio.fixture(scope="function", autouse=True)
async def init_api_config(auth_key):
    misp_api_config_data.key = auth_key[0]


@pytest.fixture(autouse=True, scope="session")
def app():
    with ExitStack():
        yield init_app()


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="class")
def client_class(request, app):
    with TestClient(app) as c:
        request.cls.client = c
        yield
