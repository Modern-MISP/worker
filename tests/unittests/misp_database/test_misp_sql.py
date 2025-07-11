import random
import uuid as libuuid
from typing import Any

import pytest
from sqlalchemy import delete, select

from mmisp.api_schemas.galaxies import RestSearchGalaxyBody
from mmisp.api_schemas.galaxy_clusters import SearchGalaxyClusterGalaxyClustersDetails
from mmisp.db.models.attribute import Attribute
from mmisp.db.models.correlation import CorrelationValue, DefaultCorrelation, OverCorrelatingValue
from mmisp.db.models.galaxy_cluster import GalaxyCluster
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.post import Post
from mmisp.tests.generators.model_generators.correlation_value_generator import generate_correlation_value
from mmisp.tests.generators.model_generators.default_correlation_generator import generate_default_correlation
from mmisp.tests.generators.model_generators.over_correlating_value_generator import generate_over_correlating_value
from mmisp.tests.generators.model_generators.post_generator import generate_post
from mmisp.util.uuid import uuid
from mmisp.worker.misp_database.misp_sql import (
    add_correlation_value,
    add_correlations,
    add_over_correlating_value,
    delete_correlations,
    delete_over_correlating_value,
    event_id_exists,
    filter_blocked_clusters,
    filter_blocked_events,
    galaxy_cluster_id_exists,
    galaxy_id_exists,
    get_api_authkey,
    get_attribute_tag_id,
    get_attributes_with_same_value,
    get_event_tag_id,
    get_excluded_correlations,
    get_number_of_correlations,
    get_org_by_name,
    get_over_correlating_values,
    get_post,
    get_threat_level,
    get_values_with_correlation,
    is_excluded_correlation,
    is_over_correlating_value,
)
from mmisp.worker.misp_dataclasses.misp_minimal_event import MispMinimalEvent


def Equal(x: Any, y: Any) -> bool:
    "helper function for migration from unittest to plain pytest"
    return x == y


def Greater(x, y) -> bool:
    return x > y


def __get_test_correlation() -> DefaultCorrelation:
    return DefaultCorrelation(
        attribute_id=10000,
        object_id=1,
        event_id=3,
        org_id=65,
        distribution=65,
        object_distribution=65,
        event_distribution=65,
        sharing_group_id=65,
        object_sharing_group_id=65,
        event_sharing_group_id=65,
        attribute_id_1=20000,
        object_id_1=65,
        event_id_1=65,
        org_id_1=65,
        distribution_1=65,
        object_distribution_1=65,
        event_distribution_1=65,
        sharing_group_id_1=65,
        object_sharing_group_id_1=65,
        event_sharing_group_id_1=65,
    )


def __get_test_cluster(cluster_uuid: str) -> SearchGalaxyClusterGalaxyClustersDetails:
    return SearchGalaxyClusterGalaxyClustersDetails(
        id=random.randint(1, 100),
        uuid=cluster_uuid,
        authors=[],
        distribution=5,
        default=False,
        locked=False,
        published=False,
        deleted=False,
        galaxy_id=1,
        version=1,
        Galaxy=RestSearchGalaxyBody(id=1),
    )


@pytest.mark.asyncio
async def __get_test_minimal_events(blocked_event_uuid: str, blocked_org_uuid: str) -> list[MispMinimalEvent]:
    response: list[MispMinimalEvent] = []
    response.append(
        MispMinimalEvent(
            id=1,
            timestamp=0,
            published=False,
            uuid=blocked_event_uuid,
            org_c_uuid="00000000-0000-0000-0000-000000000000",
        )
    )  # is blocked
    response.append(
        MispMinimalEvent(
            id=2,
            timestamp=0,
            published=False,
            uuid="fb2fa4a2-66e5-48a3-9bdd-5c5ce78e11e8",
            org_c_uuid="00000000-0000-0000-0000-000000000000",
        )
    )  # is not blocked
    response.append(
        MispMinimalEvent(
            id=3,
            timestamp=0,
            published=False,
            uuid="00000000-0000-0000-0000-000000000000",
            org_c_uuid=blocked_org_uuid,
        )
    )  # org blocked
    return response


@pytest.mark.asyncio
async def test_get_api_authkey(server, db):
    server_auth_key = server.authkey
    result: str | None = await get_api_authkey(db, server.id)
    if isinstance(result, bytes):
        result = result.decode("utf-8")
    assert result == server_auth_key


@pytest.mark.asyncio
async def test_filter_blocked_events(db, event_blocklist, org_blocklist):
    events: list[MispMinimalEvent] = await __get_test_minimal_events(event_blocklist.event_uuid, org_blocklist.org_uuid)
    result: list[MispMinimalEvent] = await filter_blocked_events(db, events, True, False)
    assert len(result) == 2
    assert result[0].id == 2
    assert result[1].id == 3
    result = await filter_blocked_events(db, events, False, True)
    assert len(result) == 2
    assert result[0].id == 1
    assert result[1].id == 2
    result = await filter_blocked_events(db, events, True, True)
    assert len(result) == 1
    assert result[0].id == 2


@pytest.mark.asyncio
async def test_filter_blocked_clusters(db, cluster_blocklist):
    uuid_cluster_one: str = uuid()
    clusters: list[SearchGalaxyClusterGalaxyClustersDetails] = [
        __get_test_cluster(uuid_cluster_one),
        __get_test_cluster(cluster_blocklist.cluster_uuid),
    ]
    result: list[SearchGalaxyClusterGalaxyClustersDetails] = await filter_blocked_clusters(db, clusters)
    assert len(result) == 1
    assert result[0].uuid == uuid_cluster_one


@pytest.mark.asyncio
async def test_get_attributes_with_same_value(db):
    result: list[Attribute] = await get_attributes_with_same_value(db, "test")
    for attribute in result:
        assert "test" == attribute.value1


@pytest.mark.asyncio
async def test_get_values_with_correlation(db, correlating_values):
    values: set[str] = {value.value for value in correlating_values}
    result: set[str] = set(await get_values_with_correlation(db))

    for value in result:
        assert value in values


@pytest.mark.asyncio
async def test_get_over_correlating_values(db, over_correlating_values):
    result: list[tuple[str, int]] = await get_over_correlating_values(db)

    for ocv in over_correlating_values:
        assert ocv.value in [value[0] for value in result]
        assert ocv.occurrence in [value[1] for value in result]

    for value in result:
        assert await is_over_correlating_value(db, value[0])
        assert value[1] > 0


@pytest.mark.asyncio
async def test_get_excluded_correlations(db, correlation_exclusions):
    result: list[str] = await get_excluded_correlations(db)

    values = [ce.value for ce in correlation_exclusions]
    for value in result:
        assert await is_excluded_correlation(db, value)
        assert value in values


@pytest.mark.asyncio
async def test_get_threat_level(db, threat_levels):
    result1: str = await get_threat_level(db, 1)
    assert result1 == "High"

    result2: str = await get_threat_level(db, 2)
    assert result2 == "Medium"

    result3: str = await get_threat_level(db, 3)
    assert result3 == "Low"

    result4: str = await get_threat_level(db, 4)
    assert result4 == "Undefined"

    result5: str = await get_threat_level(db, 5)
    assert result5 == "No threat level found"


@pytest.mark.asyncio
async def test_get_post(db, post):
    expected: Post = generate_post()
    db_post: Post = await get_post(db, post.id)
    assert Equal(db_post.user_id, expected.user_id)
    assert Equal(db_post.contents, expected.contents)
    assert Equal(db_post.post_id, expected.post_id)
    assert Equal(db_post.thread_id, expected.thread_id)

    with pytest.raises(ValueError):
        await get_post(db, 100)


@pytest.mark.asyncio
async def test_is_excluded_correlation(db, correlation_exclusion):
    assert await is_excluded_correlation(db, correlation_exclusion.value)


@pytest.mark.asyncio
async def test_is_no_excluded_correlation(db, correlation_exclusion):
    assert not await is_excluded_correlation(db, uuid())


@pytest.mark.asyncio
async def test_is_over_correlating_value(db, over_correlating_value):
    assert await is_over_correlating_value(db, over_correlating_value.value)


@pytest.mark.asyncio
async def test_is_not_over_correlating_value(db, over_correlating_value):
    assert not await is_over_correlating_value(db, uuid())


@pytest.mark.asyncio
async def test_get_number_of_correlations_over_correlating(db, over_correlating_value):
    result: int = await get_number_of_correlations(db, over_correlating_value.value, True)
    assert Equal(result, 1)


@pytest.mark.asyncio
async def test_get_number_of_correlations_default_correlating(default_correlation, db):
    statement = select(CorrelationValue.value).where(CorrelationValue.id == default_correlation.value_id)
    correlation_value: str = (await db.execute(statement)).scalar()
    await db.execute(statement)
    await db.commit()

    result: int = await get_number_of_correlations(db, correlation_value, False)
    assert Equal(result, 1)


@pytest.mark.asyncio
async def test_get_number_of_correlations_no_correlating_over_correlating(db):
    no_result: int = await get_number_of_correlations(db, uuid(), False)
    assert Equal(no_result, 0)


@pytest.mark.asyncio
async def test_get_number_of_correlations_no_correlating_default_correlating(db):
    with pytest.raises(ValueError):
        await get_number_of_correlations(db, uuid(), True)


@pytest.mark.asyncio
async def test_add_correlation_value(db):
    value: str = "test_await misp_sql"

    result: int = await add_correlation_value(db, value)
    assert Greater(result, 0)

    session = db
    statement = select(CorrelationValue).where(CorrelationValue.value == value)
    search_result: CorrelationValue = (await session.execute(statement)).scalar()
    assert Equal(search_result.value, value)
    assert Equal(search_result.id, result)

    statement = delete(CorrelationValue).where(CorrelationValue.value == value)
    await session.execute(statement)
    await session.commit()


@pytest.mark.asyncio
async def test_add_correlations(db, correlating_value):
    not_adding: list[DefaultCorrelation] = [__get_test_correlation()]
    not_adding[0].value_id = correlating_value.id
    assert await add_correlations(db, not_adding)

    not_adding1: list[DefaultCorrelation] = [__get_test_correlation()]
    not_adding1[0].value_id = correlating_value.id
    assert not await add_correlations(db, not_adding1)

    statement = delete(DefaultCorrelation).where(DefaultCorrelation.value_id == correlating_value.id)
    await db.execute(statement)


@pytest.mark.asyncio
async def test_add_over_correlating_value(db, over_correlating_value):
    occurrence: int = over_correlating_value.occurrence + 1
    assert await add_over_correlating_value(db, over_correlating_value.value, occurrence)

    statement = select(OverCorrelatingValue).where(OverCorrelatingValue.value == over_correlating_value.value)
    result: OverCorrelatingValue = (await db.execute(statement)).scalars().first()

    assert Equal(result.value, over_correlating_value.value)
    assert Equal(result.occurrence, occurrence)
    assert Equal(result.id, over_correlating_value.id)


@pytest.mark.asyncio
async def test_delete_over_correlating_value(db):
    over_correlating_value: OverCorrelatingValue = generate_over_correlating_value()
    db.add(over_correlating_value)
    await db.commit()
    await db.refresh(over_correlating_value)

    assert await delete_over_correlating_value(db, over_correlating_value.value)

    statement = select(OverCorrelatingValue).where(OverCorrelatingValue.value == over_correlating_value.value)
    result: OverCorrelatingValue = (await db.execute(statement)).first()
    assert result is None

    assert not await delete_over_correlating_value(db, over_correlating_value.value)


@pytest.mark.asyncio
async def test_delete_correlations(db):
    correlation_value: CorrelationValue = generate_correlation_value()
    db.add(correlation_value)
    await db.commit()
    await db.refresh(correlation_value)

    default_correlation: DefaultCorrelation = generate_default_correlation()
    default_correlation.value_id = correlation_value.id
    db.add(default_correlation)
    await db.commit()
    await db.refresh(default_correlation)

    statement = select(CorrelationValue.value).where(CorrelationValue.id == default_correlation.value_id)
    value = (await db.execute(statement)).scalar()

    amount: int = await get_number_of_correlations(db, value, False)
    assert Equal(1, amount)

    assert await delete_correlations(db, value)

    amount = await get_number_of_correlations(db, value, False)
    assert Equal(0, amount)

    statement = select(CorrelationValue).where(CorrelationValue.value == value)
    result: CorrelationValue | None = (await db.execute(statement)).first()
    assert result is None


@pytest.mark.asyncio
async def test_get_event_tag_id(db, event_with_normal_tag):
    exists = await get_event_tag_id(db, event_with_normal_tag[0].id, event_with_normal_tag[1].tag_id)
    assert Equal(exists, event_with_normal_tag[1].id)
    not_exists = await get_event_tag_id(db, 1, 100)
    assert Equal(not_exists, -1)


@pytest.mark.asyncio
async def test_get_attribute_tag_id(db, attribute_with_normal_tag):
    at_id = await get_attribute_tag_id(db, attribute_with_normal_tag[0].id, attribute_with_normal_tag[1].tag_id)
    assert Equal(at_id, attribute_with_normal_tag[1].id)

    not_exists = await get_attribute_tag_id(db, 1, 100)
    assert Equal(not_exists, -1)


@pytest.mark.asyncio
async def test_event_id_exists(db, event):
    assert await event_id_exists(db, event.id)
    assert await event_id_exists(db, str(event.uuid))
    assert not await event_id_exists(db, uuid())


@pytest.mark.asyncio
async def test_galaxy_id_exists(db, galaxy):
    assert await galaxy_id_exists(db, galaxy.id)
    assert await galaxy_id_exists(db, libuuid.UUID(galaxy.uuid))
    assert not await galaxy_id_exists(db, libuuid.uuid4())


@pytest.mark.asyncio
async def test_galaxy_cluster_id_exists(db, test_galaxy):
    cluster: GalaxyCluster = test_galaxy["galaxy_cluster"]
    assert await galaxy_cluster_id_exists(db, cluster.id)
    assert await galaxy_cluster_id_exists(db, libuuid.UUID(cluster.uuid))
    assert not await galaxy_cluster_id_exists(db, libuuid.uuid4())


@pytest.mark.asyncio
async def test_get_org_by_name(db, organisation):
    org: Organisation | None = await get_org_by_name(db, organisation.name)
    assert org
    assert org.uuid == organisation.uuid
    assert org.name == organisation.name
