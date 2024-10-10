from contextlib import ExitStack

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from icecream import ic

from mmisp.tests.fixtures import *  # noqa
from mmisp.worker.main import init_app
from mmisp.worker.misp_database.misp_api_config import misp_api_config_data


@pytest_asyncio.fixture
async def init_api_config(auth_key):
    ic(auth_key)
    misp_api_config_data.key = auth_key[0]


@pytest.fixture(autouse=True)
def app():
    with ExitStack():
        yield init_app()


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture
def client_class(request, app):
    with TestClient(app) as c:
        request.cls.client = c
