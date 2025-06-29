import uuid as libuuid
from contextlib import AsyncExitStack
from datetime import date, datetime, timedelta

import pytest_asyncio
from sqlalchemy import delete, or_, select
from sqlalchemy.orm import selectinload

from mmisp.db.database import DatabaseSessionManager
from mmisp.db.models.attribute import Attribute
from mmisp.db.models.event import Event
from mmisp.db.models.galaxy import Galaxy
from mmisp.db.models.galaxy_cluster import GalaxyCluster, GalaxyElement
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.server import Server
from mmisp.db.models.sighting import Sighting
from mmisp.lib.distribution import DistributionLevels, EventDistributionLevels
from mmisp.lib.galaxies import galaxy_tag_name
from mmisp.tests.fixtures import DBManager, auth_key
from mmisp.tests.generators.model_generators.attribute_generator import generate_attribute, generate_random_attribute
from mmisp.tests.generators.model_generators.organisation_generator import generate_organisation
from mmisp.tests.generators.model_generators.role_generator import generate_site_admin_role
from mmisp.tests.generators.model_generators.shadow_attribute_generator import generate_shadow_attribute
from mmisp.tests.generators.model_generators.sighting_generator import generate_sighting
from mmisp.tests.generators.model_generators.user_generator import generate_user
from mmisp.tests.generators.model_generators.user_setting_generator import generate_user_name
from mmisp.util.uuid import uuid
from mmisp.worker.exceptions.misp_api_exceptions import InvalidAPIResponse


@pytest_asyncio.fixture
async def remote_auth_key(remote_db, remote_site_admin_user):
    async for e in auth_key(remote_db, remote_site_admin_user):
        yield e


@pytest_asyncio.fixture
async def remote_misp(db, instance_owner_org, remote_instance_owner_org, remote_auth_key):
    server = Server(
        name="misp-core-remote",
        url="http://misp-core-remote",
        authkey="siteadminuser".ljust(40, "0"),
        org_id=instance_owner_org.id,
        push=True,
        pull=True,
        push_sightings=True,
        push_galaxy_clusters=True,
        pull_galaxy_clusters=True,
        push_analyst_data=True,
        pull_analyst_data=True,
        last_pulled_id=0,
        last_pushed_id=0,
        organization="ORG",
        remote_org_id=remote_instance_owner_org.id,
        self_signed=False,
        pull_rules="",
        push_rules="",
    )

    db.add(server)
    await db.commit()
    await db.refresh(server)
    yield server
    await db.delete(server)
    await db.commit()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def remote_db_connection():
    sm = DatabaseSessionManager("mysql+aiomysql://root:misp@db:3306/misp_remote")
    sm.init()
    await sm.create_all()
    yield sm


@pytest_asyncio.fixture
async def remote_db(remote_db_connection):
    async with remote_db_connection.session() as session:
        yield session


@pytest_asyncio.fixture
async def remote_instance_owner_org(remote_db):
    instance_owner_org = generate_organisation()
    remote_db.add(instance_owner_org)
    await remote_db.commit()
    await remote_db.refresh(instance_owner_org)
    yield instance_owner_org
    await remote_db.delete(instance_owner_org)
    await remote_db.commit()


@pytest_asyncio.fixture
async def remote_site_admin_user(remote_db, remote_site_admin_role, remote_instance_owner_org):
    assert remote_instance_owner_org.local

    user = generate_user()
    user.org_id = remote_instance_owner_org.id
    user.server_id = 0
    user.role_id = remote_site_admin_role.id

    remote_db.add(user)
    await remote_db.commit()
    await remote_db.refresh(user)

    user_setting = generate_user_name()
    user_setting.user_id = user.id

    remote_db.add(user_setting)
    await remote_db.commit()

    yield user
    await remote_db.delete(user_setting)
    await remote_db.commit()
    await remote_db.delete(user)
    await remote_db.commit()


@pytest_asyncio.fixture
async def remote_event(remote_db, remote_organisation, remote_site_admin_user):
    org_id = remote_organisation.id
    event = Event(
        org_id=org_id,
        orgc_id=org_id,
        user_id=remote_site_admin_user.id,
        uuid=libuuid.uuid4(),
        sharing_group_id=0,
        threat_level_id=1,
        info="test event",
        date=date(year=2024, month=2, day=13),
        analysis=1,
        distribution=EventDistributionLevels.ALL_COMMUNITIES,
        published=1,
    )

    remote_db.add(event)
    await remote_db.commit()
    await remote_db.refresh(event)

    yield event

    await remote_db.commit()
    await remote_db.delete(event)
    await remote_db.commit()


@pytest_asyncio.fixture
async def remote_event2(remote_db, remote_organisation, remote_site_admin_user):
    org_id = remote_organisation.id
    event = Event(
        org_id=org_id,
        orgc_id=org_id,
        user_id=remote_site_admin_user.id,
        uuid=libuuid.uuid4(),
        sharing_group_id=0,
        threat_level_id=1,
        info="test event",
        date=date(year=2024, month=2, day=13),
        analysis=1,
        distribution=EventDistributionLevels.ALL_COMMUNITIES,
        published=1,
    )

    remote_db.add(event)
    await remote_db.commit()
    await remote_db.refresh(event)

    yield event

    await remote_db.delete(event)
    await remote_db.commit()


@pytest_asyncio.fixture
async def remote_sighting(remote_db, remote_organisation, remote_event_with_attributes):
    attribute: Attribute = remote_event_with_attributes.attributes[0]
    sighting: Sighting = generate_sighting(remote_event_with_attributes.id, attribute.id, remote_organisation.id)

    remote_db.add(sighting)
    await remote_db.commit()
    await remote_db.refresh(sighting)

    yield sighting

    await remote_db.delete(sighting)
    await remote_db.commit()


@pytest_asyncio.fixture
async def remote_site_admin_role(remote_db):
    role = generate_site_admin_role()
    remote_db.add(role)
    await remote_db.commit()
    await remote_db.refresh(role)
    yield role
    await remote_db.delete(role)
    await remote_db.commit()


@pytest_asyncio.fixture
async def remote_organisation(remote_db):
    organisation = generate_organisation()

    remote_db.add(organisation)
    await remote_db.commit()
    await remote_db.refresh(organisation)

    yield organisation

    await remote_db.delete(organisation)
    await remote_db.commit()


@pytest_asyncio.fixture()
async def remote_event_with_attributes(remote_db, remote_event):
    event_id = remote_event.id
    attribute = generate_attribute(event_id)
    attribute_2 = generate_attribute(event_id)
    remote_event.attribute_count += 2

    remote_db.add(attribute)
    remote_db.add(attribute_2)
    await remote_db.commit()
    await remote_db.refresh(remote_event)

    qry = (
        select(Event)
        .filter(Event.id == event_id)
        .options(selectinload(Event.attributes))
        .execution_options(populate_existing=True)
    )
    await remote_db.execute(qry)

    await remote_db.refresh(attribute)
    await remote_db.refresh(attribute_2)

    yield remote_event

    await remote_db.delete(attribute)
    await remote_db.delete(attribute_2)
    remote_event.attribute_count -= 2

    await remote_db.commit()


@pytest_asyncio.fixture
async def remote_shadow_attribute(remote_db, remote_organisation, remote_event):
    shadow_attribute = generate_shadow_attribute(
        remote_organisation.id, remote_event.id, remote_event.uuid, remote_event.org_id
    )

    remote_db.add(shadow_attribute)
    await remote_db.commit()
    await remote_db.refresh(shadow_attribute)

    yield shadow_attribute

    await remote_db.delete(shadow_attribute)
    await remote_db.commit()


@pytest_asyncio.fixture
async def remote_test_galaxy(remote_db, remote_instance_owner_org, galaxy_cluster_one_uuid, galaxy_cluster_two_uuid):
    async with AsyncExitStack() as stack:

        async def add_to_db(elem):
            return await stack.enter_async_context(DBManager(remote_db, elem))

        galaxy = await add_to_db(
            Galaxy(
                namespace="misp",
                name="test galaxy",
                type="test galaxy type",
                description="test",
                version="1",
                kill_chain_order=None,
                uuid=uuid(),
                enabled=True,
                local_only=False,
                org_id=remote_instance_owner_org.id,
                orgc_id=remote_instance_owner_org.id,
                distribution=DistributionLevels.ALL_COMMUNITIES,
                created=datetime.now(),
                modified=datetime.now(),
            )
        )

        remote_db.add(galaxy)
        await remote_db.commit()
        await remote_db.refresh(galaxy)

        galaxy_cluster = await add_to_db(
            GalaxyCluster(
                uuid=galaxy_cluster_one_uuid,
                collection_uuid="",
                type="test galaxy type",
                value="test",
                tag_name=galaxy_tag_name("test galaxy type", galaxy_cluster_one_uuid),
                description="test",
                galaxy_id=galaxy.id,
                source="me",
                authors=["Konstantin Zangerle", "Test Writer"],
                version=1,
                distribution=DistributionLevels.ALL_COMMUNITIES,
                sharing_group_id=None,
                org_id=remote_instance_owner_org.id,
                orgc_id=remote_instance_owner_org.id,
                default=0,
                locked=0,
                extends_uuid=None,
                extends_version=None,
                published=True,
                deleted=False,
            )
        )
        galaxy_cluster2 = await add_to_db(
            GalaxyCluster(
                uuid=galaxy_cluster_two_uuid,
                collection_uuid="",
                type="test galaxy type",
                value="test",
                tag_name=galaxy_tag_name("test galaxy type", galaxy_cluster_two_uuid),
                description="test",
                galaxy_id=galaxy.id,
                source="me",
                authors=["Konstantin Zangerle", "Test Writer"],
                version=1,
                distribution=3,
                sharing_group_id=None,
                org_id=remote_instance_owner_org.id,
                orgc_id=remote_instance_owner_org.id,
                default=0,
                locked=0,
                extends_uuid=None,
                extends_version=None,
                published=True,
                deleted=False,
            )
        )

        galaxy_element = GalaxyElement(
            galaxy_cluster_id=galaxy_cluster.id, key="refs", value="http://test-one-one.example.com"
        )
        galaxy_element2 = GalaxyElement(
            galaxy_cluster_id=galaxy_cluster.id, key="refs", value="http://test-one-two.example.com"
        )

        galaxy_element21 = GalaxyElement(
            galaxy_cluster_id=galaxy_cluster2.id, key="refs", value="http://test-two-one.example.com"
        )
        galaxy_element22 = GalaxyElement(
            galaxy_cluster_id=galaxy_cluster2.id, key="refs", value="http://test-two-two.example.com"
        )

        galaxy_elements = (galaxy_element, galaxy_element2, galaxy_element21, galaxy_element22)
        for g_e in galaxy_elements:
            remote_db.add(g_e)

        await remote_db.commit()

        for g_e in galaxy_elements:
            await remote_db.refresh(g_e)

        yield {
            "galaxy": galaxy,
            "galaxy_cluster": galaxy_cluster,
            "galaxy_cluster2": galaxy_cluster2,
            "galaxy_element": galaxy_element,
            "galaxy_element2": galaxy_element2,
            "galaxy_element21": galaxy_element21,
            "galaxy_element22": galaxy_element22,
        }

        await remote_db.commit()

        # if a galaxy cluster is edited, new elements are created with new IDs, therefore we need this
        qry = delete(GalaxyElement).where(GalaxyElement.galaxy_cluster_id.in_([galaxy_cluster.id, galaxy_cluster2.id]))
        await remote_db.execute(qry)


@pytest_asyncio.fixture
async def remote_sharing_group(remote_db, sharing_group):
    remote_db.add(sharing_group)

    await remote_db.commit()
    await remote_db.refresh(sharing_group)

    yield sharing_group

    await remote_db.delete(sharing_group)
    await remote_db.commit()


@pytest_asyncio.fixture
async def pull_job_remote_event(db, user, remote_organisation, remote_event):
    local_org: Organisation = Organisation(
        name=remote_organisation.name,
        uuid=remote_organisation.uuid,
        description=remote_organisation.description,
        type=remote_organisation.type,
        nationality=remote_organisation.nationality,
        sector=remote_organisation.sector,
        created_by=user.id,
        contacts=remote_organisation.contacts,
        local=remote_organisation.local,
        restricted_to_domain=remote_organisation.restricted_to_domain,
        landingpage=remote_organisation.landingpage,
    )

    db.add(local_org)
    await db.commit()
    await db.refresh(local_org)

    yield remote_event

    await db.commit()

    statement = delete(Event).where(Event.uuid == remote_event.uuid)
    await db.execute(statement)

    await db.delete(local_org)
    await db.commit()


@pytest_asyncio.fixture
async def pull_job_remote_galaxy_cluster(db, remote_misp, remote_test_galaxy):
    # Add galaxy with same uuid to local server. Galaxy pull not yet implemented.
    galaxy: Galaxy = remote_test_galaxy["galaxy"]
    local_galaxy: Galaxy = Galaxy(
        uuid=galaxy.uuid,
        name=galaxy.name,
        type=galaxy.type,
        description=galaxy.description,
        version=galaxy.version,
        org_id=remote_misp.org_id,
        orgc_id=remote_misp.org_id,
        distribution=galaxy.distribution,
        created=galaxy.created,
        modified=galaxy.modified,
    )

    db.add(local_galaxy)
    await db.commit()
    await db.refresh(local_galaxy)

    yield remote_test_galaxy

    statement = delete(GalaxyCluster).where(
        or_(
            GalaxyCluster.uuid == remote_test_galaxy["galaxy_cluster"].uuid,
            GalaxyCluster.uuid == remote_test_galaxy["galaxy_cluster2"].uuid,
        )
    )
    await db.execute(statement)

    await db.delete(local_galaxy)
    await db.commit()


@pytest_asyncio.fixture
async def pull_job_remote_cluster_with_new_orgc(
    db, galaxy_cluster_one_uuid, remote_db, remote_organisation, remote_misp
):
    galaxy_dict = {
        "namespace": "misp",
        "name": "test galaxy",
        "type": "test galaxy type",
        "description": "test",
        "version": "1",
        "kill_chain_order": None,
        "uuid": uuid(),
        "enabled": True,
        "local_only": False,
        "distribution": DistributionLevels.ALL_COMMUNITIES,
        "created": datetime.now(),
        "modified": datetime.now(),
    }

    remote_galaxy: Galaxy = Galaxy(**galaxy_dict, org_id=remote_organisation.id, orgc_id=remote_organisation.id)
    remote_db.add(remote_galaxy)
    await remote_db.commit()
    await remote_db.refresh(remote_galaxy)

    # Add galaxy with same uuid to local server. Galaxy pull not yet implemented.
    local_galaxy: Galaxy = Galaxy(**galaxy_dict, org_id=remote_misp.org_id, orgc_id=remote_misp.org_id)
    db.add(local_galaxy)
    await db.commit()
    await db.refresh(local_galaxy)

    remote_cluster = GalaxyCluster(
        uuid=galaxy_cluster_one_uuid,
        collection_uuid="",
        type="test galaxy type",
        value="test",
        tag_name=galaxy_tag_name("test galaxy type", galaxy_cluster_one_uuid),
        description="test",
        galaxy_id=remote_galaxy.id,
        source="me",
        authors=["Konstantin Zangerle", "Test Writer"],
        version=1,
        distribution=3,
        sharing_group_id=None,
        org_id=remote_organisation.id,
        orgc_id=remote_organisation.id,
        default=0,
        locked=0,
        extends_uuid=None,
        extends_version=None,
        published=True,
        deleted=False,
    )

    remote_db.add(remote_cluster)
    await remote_db.commit()
    await remote_db.refresh(remote_cluster)

    yield remote_cluster

    await db.flush()
    await remote_db.flush()

    await remote_db.delete(remote_cluster)
    await remote_db.delete(remote_galaxy)
    await remote_db.commit()

    await db.execute(delete(GalaxyCluster).where(GalaxyCluster.uuid == galaxy_cluster_one_uuid))

    await db.delete(local_galaxy)
    await db.commit()


@pytest_asyncio.fixture
async def set_server_version(remote_misp, remote_db, misp_api):
    # uuid of misp server is null after initialization of server, after calling get_server_version it is set
    try:
        await misp_api.get_server_version(remote_misp)
    except InvalidAPIResponse:
        pass


@pytest_asyncio.fixture()
async def sync_test_event(db, event, site_admin_user, sharing_group, remote_db):
    event.published = True
    event.user_id = site_admin_user.id
    event.sharing_group_id = sharing_group.id
    event_id = event.id
    attribute = generate_random_attribute(event_id)
    attribute_2 = generate_random_attribute(event_id)
    event.attribute_count += 2
    event.timestamp = datetime.now() - timedelta(seconds=10)

    db.add(event)
    await db.commit()

    db.add(attribute)
    db.add(attribute_2)
    await db.commit()
    await db.refresh(event)
    await db.refresh(attribute)
    await db.refresh(attribute_2)

    qry = (
        select(Event)
        .filter(Event.id == event_id)
        .options(selectinload(Event.attributes))
        .execution_options(populate_existing=True)
    )
    await db.execute(qry)

    await db.refresh(attribute)
    await db.refresh(attribute_2)

    yield event

    await db.delete(attribute)
    await db.delete(attribute_2)

    await db.commit()

    # pushed event cleanup at remote db
    await remote_db.commit()
    async with remote_db.begin():
        await remote_db.execute(delete(Event).where(Event.uuid == event.uuid))
        await remote_db.execute(delete(Attribute).where(Attribute.uuid.in_([attribute.uuid, attribute_2.uuid])))


@pytest_asyncio.fixture
async def push_galaxy(
    db, instance_owner_org, galaxy_cluster_one_uuid, galaxy_cluster_two_uuid, remote_db, remote_instance_owner_org
):
    galaxy_uuid: str = uuid()
    galaxy = Galaxy(
        namespace="misp",
        name="test galaxy",
        type="test galaxy type",
        description="test",
        version="1",
        kill_chain_order=None,
        uuid=galaxy_uuid,
        enabled=True,
        local_only=False,
        org_id=1,
        orgc_id=1,
        distribution=DistributionLevels.ALL_COMMUNITIES,
        created=datetime.now(),
        modified=datetime.now(),
    )

    remote_galaxy = Galaxy(
        namespace="misp",
        name="test galaxy",
        type="test galaxy type",
        description="test",
        version="1",
        kill_chain_order=None,
        uuid=galaxy_uuid,
        enabled=True,
        local_only=False,
        org_id=2,
        orgc_id=2,
        distribution=DistributionLevels.ALL_COMMUNITIES,
        created=datetime.now(),
        modified=datetime.now(),
    )

    db.add(galaxy)
    await db.commit()
    await db.refresh(galaxy)

    remote_db.add(remote_galaxy)
    await remote_db.commit()
    await remote_db.refresh(remote_galaxy)

    galaxy_cluster = GalaxyCluster(
        uuid=galaxy_cluster_one_uuid,
        collection_uuid="",
        type="test galaxy type",
        value="test",
        tag_name=galaxy_tag_name("test galaxy type", galaxy_cluster_one_uuid),
        description="test",
        galaxy_id=galaxy.id,
        source="me",
        authors=["Konstantin Zangerle", "Test Writer"],
        version=1,
        distribution=3,
        sharing_group_id=None,
        org_id=instance_owner_org.id,
        orgc_id=instance_owner_org.id,
        default=0,
        locked=0,
        extends_uuid=None,
        extends_version=None,
        published=True,
        deleted=False,
    )
    galaxy_cluster2 = GalaxyCluster(
        uuid=galaxy_cluster_two_uuid,
        collection_uuid="",
        type="test galaxy type",
        value="test",
        tag_name=galaxy_tag_name("test galaxy type", galaxy_cluster_two_uuid),
        description="test",
        galaxy_id=galaxy.id,
        source="me",
        authors=["Konstantin Zangerle", "Test Writer"],
        version=1,
        distribution=3,
        sharing_group_id=None,
        org_id=instance_owner_org.id,
        orgc_id=instance_owner_org.id,
        default=0,
        locked=0,
        extends_uuid=None,
        extends_version=None,
        published=True,
        deleted=False,
    )

    db.add(galaxy_cluster)
    db.add(galaxy_cluster2)

    await db.commit()
    await db.refresh(galaxy_cluster)
    await db.refresh(galaxy_cluster2)

    galaxy_element = GalaxyElement(
        galaxy_cluster_id=galaxy_cluster.id, key="refs", value="http://test-one-one.example.com"
    )
    galaxy_element2 = GalaxyElement(
        galaxy_cluster_id=galaxy_cluster.id, key="refs", value="http://test-one-two.example.com"
    )

    galaxy_element21 = GalaxyElement(
        galaxy_cluster_id=galaxy_cluster2.id, key="refs", value="http://test-two-one.example.com"
    )
    galaxy_element22 = GalaxyElement(
        galaxy_cluster_id=galaxy_cluster2.id, key="refs", value="http://test-two-two.example.com"
    )

    db.add(galaxy_element)
    db.add(galaxy_element2)

    db.add(galaxy_element21)
    db.add(galaxy_element22)

    await db.commit()

    yield {
        "galaxy": galaxy,
        "galaxy_cluster": galaxy_cluster,
        "galaxy_cluster2": galaxy_cluster2,
        "galaxy_element": galaxy_element,
        "galaxy_element2": galaxy_element2,
        "galaxy_element21": galaxy_element21,
        "galaxy_element22": galaxy_element22,
    }

    await db.delete(galaxy_element22)
    await db.delete(galaxy_element21)
    await db.delete(galaxy_element2)
    await db.delete(galaxy_element)
    await db.commit()
    await db.delete(galaxy_cluster2)
    await db.delete(galaxy_cluster)
    await db.commit()
    await db.delete(galaxy)
    await db.commit()

    await remote_db.commit()
    await remote_db.execute(
        delete(GalaxyCluster).where(GalaxyCluster.uuid.in_([galaxy_cluster.uuid, galaxy_cluster2.uuid]))
    )
    await remote_db.delete(remote_galaxy)
