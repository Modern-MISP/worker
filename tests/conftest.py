import logging
from contextlib import ExitStack

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from icecream import ic

from mmisp.tests.fixtures import *  # noqa
from mmisp.worker.config import system_config_data
from mmisp.worker.main import init_app
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_api_config import misp_api_config_data


@pytest.fixture
def worker_disabled():
    yield


@pytest_asyncio.fixture
async def init_api_config(auth_key):
    ic(auth_key)
    misp_api_config_data.key = auth_key[0]


@pytest_asyncio.fixture
async def misp_api(db, init_api_config):
    return MispAPI(db)


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


class SQLFilter(logging.Filter):
    def filter(self, record):
        # Suppress specific query pattern
        if "SELECT COUNT(*) FROM information_schema.tables" in record.getMessage():
            return False
        return True


# Add filter to the SQLAlchemy logger
logger = logging.getLogger("sqlalchemy.engine")
logger.addFilter(SQLFilter())
