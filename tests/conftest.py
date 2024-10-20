from contextlib import ExitStack

from celery.app.control import Control
from fastapi.testclient import TestClient
from icecream import ic

from mmisp.tests.fixtures import *  # noqa
from mmisp.worker.config import system_config_data
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.main import init_app
from mmisp.worker.misp_database.misp_api_config import misp_api_config_data


@pytest.fixture
def worker_disabled():
    Control(celery_app).broadcast("pause_consume_from_all_queues")
    yield
    Control(celery_app).broadcast("reset_worker_queues")


@pytest_asyncio.fixture
async def init_api_config(auth_key):
    ic(auth_key)
    misp_api_config_data.key = auth_key[0]


@pytest.fixture
def authorization_headers(init_api_config):
    return {"Authorization": f"Bearer {system_config_data.api_key}"}


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
