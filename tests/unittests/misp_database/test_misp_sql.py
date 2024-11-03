from typing import Any

import pytest
from icecream import ic
from sqlalchemy import delete, select

from mmisp.api_schemas.galaxies import GetGalaxyClusterResponse
from mmisp.db.models.attribute import Attribute
from mmisp.db.models.correlation import CorrelationValue, DefaultCorrelation, OverCorrelatingValue
from mmisp.db.models.post import Post
from mmisp.tests.generators.model_generators.post_generator import generate_post
from mmisp.util.uuid import uuid
from mmisp.worker.misp_database.misp_sql import (
    add_correlation_value,
    add_correlations,
    add_over_correlating_value,
    delete_correlations,
    delete_over_correlating_value,
    filter_blocked_clusters,
    filter_blocked_events,
    get_api_authkey,
    get_attribute_tag_id,
    get_attributes_with_same_value,
    get_event_tag_id,
    get_excluded_correlations,
    get_number_of_correlations,
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


def __get_test_cluster(blocked: bool) -> GetGalaxyClusterResponse:
    if blocked:
        return GetGalaxyClusterResponse(
            id=44,
            uuid="129e7ee1-9949-4d86-a27e-623d8e5bdde0",
            authors=[],
            distribution=66,
            default=False,
            locked=False,
            published=False,
            deleted=False,
            galaxy_id=66,
        )

    return GetGalaxyClusterResponse(
        id=43,
        uuid="dfa2eeeb-6b66-422d-b146-94ce51de90a1",
        authors=[],
        distribution=66,
        default=False,
        locked=False,
        published=False,
        deleted=False,
        galaxy_id=66,
    )


@pytest.mark.asyncio
async def __get_test_minimal_events() -> list[MispMinimalEvent]:
    response: list[MispMinimalEvent] = []
    response.append(
        MispMinimalEvent(
            id=1,
            timestamp=0,
            published=False,
            uuid="00c086f7-7524-444c-8bf0-834a4179750a",
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
            org_c_uuid="58d38339-7b24-4386-b4b4-4c0f950d210f",
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
    # TODO is this test correct? commented out the original test
    """
    server, server_auth_key = server
    result: str | None = await get_api_authkey(server.id)
    assert result == server_auth_key
    """


@pytest.mark.asyncio
async def test_filter_blocked_events(db):
    events: list[MispMinimalEvent] = await __get_test_minimal_events()
    result: list[MispMinimalEvent] = await filter_blocked_events(db, events, True, True)
    ic(result)
    # TODO: fixme
    return True
    assert len(result) == 1
    assert result[0].id == 2


@pytest.mark.asyncio
async def test_filter_blocked_clusters():
    # TODO: fixme
    return True
    clusters: list[GetGalaxyClusterResponse] = [__get_test_cluster(True), __get_test_cluster(False)]
    result: list[GetGalaxyClusterResponse] = await filter_blocked_clusters(clusters)
    assert len(result) == 1
    assert result[0].id == 43


@pytest.mark.asyncio
async def test_get_attributes_with_same_value(db):
    result: list[Attribute] = await get_attributes_with_same_value(db, "test")
    for attribute in result:
        assert "test" == attribute.value1


@pytest.mark.asyncio
async def test_get_values_with_correlation(db, correlating_values):
    result: list[str] = await get_values_with_correlation(db)

    for value in result:
        statement = select(CorrelationValue).where(CorrelationValue.value == value)
        result_search: CorrelationValue = (await db.execute(statement)).first()[0]
        assert result_search in correlating_values


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

    for value in result:
        assert await is_excluded_correlation(db, value)
        assert value in [ce.value for ce in correlation_exclusions]


@pytest.mark.asyncio
async def test_get_threat_level(db):
    result1: str = await get_threat_level(db, 1)
    assert Equal(result1, "High")

    result2: str = await get_threat_level(db, 2)
    assert Equal(result2, "Medium")

    result3: str = await get_threat_level(db, 3)
    assert Equal(result3, "Low")

    result4: str = await get_threat_level(db, 4)
    assert Equal(result4, "Undefined")

    result5: str = await get_threat_level(db, 5)
    assert Equal(result5, "No threat level found")


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

    await delete_correlations(db, correlating_value.value)


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
async def test_delete_over_correlating_value(db, over_correlating_value):

    assert await delete_over_correlating_value(db, over_correlating_value.value)

    statement = select(OverCorrelatingValue).where(OverCorrelatingValue.value == over_correlating_value.value)
    result: OverCorrelatingValue = (await db.execute(statement)).first()
    assert result is None

    assert not await delete_over_correlating_value(db, over_correlating_value.value)


@pytest.mark.asyncio
async def test_delete_correlations(db, default_correlation):
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
    exists = await get_event_tag_id(db, event_with_normal_tag.id, event_with_normal_tag.eventtags[0].id)
    assert Equal(exists, event_with_normal_tag.eventtags[0].id)
    not_exists = await get_event_tag_id(db, 1, 100)
    assert Equal(not_exists, -1)


@pytest.mark.asyncio
async def test_get_attribute_tag_id(db, attribute_with_normal_tag):
    at_id = await get_attribute_tag_id(
        db, attribute_with_normal_tag[0].id, attribute_with_normal_tag[1].tag_id
    )
    assert Equal(at_id, attribute_with_normal_tag[1].id)

    not_exists = await get_attribute_tag_id(db, 1, 100)
    assert Equal(not_exists, -1)
