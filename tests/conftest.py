import asyncio
import string
from contextlib import ExitStack
from time import time, time_ns

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from nanoid import generate

from mmisp.db.database import DatabaseSessionManager, sessionmanager
from mmisp.db.models.auth_key import AuthKey
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.role import Role
from mmisp.db.models.server import Server
from mmisp.db.models.user import User
from mmisp.util.crypto import hash_secret
from mmisp.util.uuid import uuid
from mmisp.worker.main import init_app


@pytest.fixture(autouse=True)
def app():
    with ExitStack():
        yield init_app()


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


# @pytest_asyncio.fixture(scope="session", autouse=True)
# def start_server(app):
#    def run_server():
#        config: Config = uvicorn.Config(app, host="localhost", port=8000, log_level="info")
#        server: uvicorn.Server = uvicorn.Server(config)
#        asyncio.run(server.serve())
#
#    process = Process(target=run_server)
#    process.start()
#    sleep(2)
#    yield
#    process.terminate()
#    process.join()


@pytest_asyncio.fixture(scope="session", autouse=True)
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def db_connection(event_loop):
    sm = DatabaseSessionManager()
    sm.init()
    await sm.create_all()
    yield sm


@pytest_asyncio.fixture
async def db(db_connection):
    async with db_connection.session() as session:
        yield session


@pytest_asyncio.fixture
async def site_admin_role(db):
    role = Role(
        name="Site Admin Role",
        perm_add=True,
        perm_modify=True,
        perm_modify_org=True,
        perm_publish=True,
        perm_delegate=True,
        perm_sync=True,
        perm_admin=True,
        perm_audit=True,
        perm_auth=True,
        perm_site_admin=True,
        perm_regexp_access=True,
        perm_tagger=True,
        perm_template=True,
        perm_sharing_group=True,
        perm_tag_editor=True,
        perm_sighting=True,
        perm_object_template=True,
        default_role=False,
        memory_limit="",
        max_execution_time="",
        restricted_to_site_admin=False,
        perm_publish_zmq=True,
        perm_publish_kafka=True,
        perm_decaying=True,
        enforce_rate_limit=False,
        rate_limit_count=0,
        perm_galaxy_editor=True,
        perm_warninglist=True,
        perm_view_feed_correlations=True,
    )
    db.add(role)
    await db.commit()
    yield role
    db.delete(role)
    await db.commit()


@pytest_asyncio.fixture
async def site_admin_user(db, site_admin_role):
    user = User(
        password=hash_secret("test"),
        email=f"generated-user+{time_ns()}@test.com",
        autoalert=False,
        authkey="auth key",
        invited_by=0,
        gpgkey="",
        certif_public="",
        nids_sid=12345,  # unused
        termsaccepted=True,
        newsread=0,
        change_pw=False,
        contactalert=False,
        disabled=False,
        expiration=None,
        current_login=time(),
        last_login=time(),
        force_logout=False,
        role_id=site_admin_role.id,
    )
    db.add(user)
    await db.commit()
    yield user
    db.delete(user)
    await db.commit()


@pytest_asyncio.fixture
async def admin_auth_key(db, site_admin_user):
    clear_key = generate(string.ascii_letters + string.digits, size=40)
    auth_key = AuthKey(
        authkey=hash_secret(clear_key),
        authkey_start=clear_key[:4],
        authkey_end=clear_key[-4:],
        comment="test comment",
    )
    auth_key.user_id = site_admin_user.id

    db.add(auth_key)
    await db.commit()

    yield clear_key, auth_key

    db.delete(auth_key)
    await db.commit()


@pytest_asyncio.fixture
async def remote_org(db):
    org = Organisation(
        name=f"unique-{time()}-{uuid()}",
        description="auto-generated org",
        type="another free text description",
        nationality="earthian",
        sector="software",
        created_by=0,
        contacts="Test Org\r\nBuilding 42\r\nAdenauerring 7\r\n76131 Karlsruhe\r\nGermany",
        local=False,
        restricted_to_domain="",
        landingpage="",
        uuid=str(uuid()),
    )
    db.add(org)
    await db.commit()
    yield org

    await db.delete(org)
    await db.commit()


@pytest_asyncio.fixture
async def server(db, remote_org):
    server_auth_key = generate(string.ascii_letters + string.digits, size=40)
    server = Server(
        name=f"test server {time()}-{uuid()}",
        url=f"http://{time()}-{uuid()}.server.mmisp.service",
        authkey=server_auth_key,
        push=False,
        pull=False,
        push_sightings=False,
        org_id=remote_org.id,
        remote_org_id=remote_org.id,
        self_signed=False,
        pull_rules="",
        push_rules="",
    )

    db.add(server)
    await db.commit()

    yield server, server_auth_key

    await db.delete(server)
    await db.commit()


sessionmanager.init()
