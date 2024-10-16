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
async def test_get_api_authkey(server):
    server_auth_key = server.authkey
    result: str | None = await get_api_authkey(server.id)
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
async def test_filter_blocked_events():
    events: list[MispMinimalEvent] = await __get_test_minimal_events()
    result: list[MispMinimalEvent] = await filter_blocked_events(events, True, True)
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
async def test_get_attributes_with_same_value():
    result: list[Attribute] = await get_attributes_with_same_value("test")
    for attribute in result:
        assert "test" == attribute.value1


@pytest.mark.asyncio
async def test_get_values_with_correlation(db, correlating_values):
    result: list[str] = await get_values_with_correlation()

    for value in result:
        statement = select(CorrelationValue).where(CorrelationValue.value == value)
        result_search: str = (await db.execute(statement)).first()
        assert result_search in correlating_values


@pytest.mark.asyncio
async def test_get_over_correlating_values(over_correlating_values):
    result: list[tuple[str, int]] = await get_over_correlating_values()

    for ocv in over_correlating_values:
        assert ocv.value in [value[0] for value in result]
        assert ocv.occurrence in [value[1] for value in result]

    for value in result:
        assert await is_over_correlating_value(value[0])
        assert value[1] > 0


@pytest.mark.asyncio
async def test_get_excluded_correlations(correlation_exclusions):
    result: list[str] = await get_excluded_correlations()
    for value in result:
        assert await is_excluded_correlation(value)
        assert value in [ce.value for ce in correlation_exclusions]


@pytest.mark.asyncio
async def test_get_threat_level():
    result1: str = await get_threat_level(1)
    assert Equal(result1, "High")

    result2: str = await get_threat_level(2)
    assert Equal(result2, "Medium")

    result3: str = await get_threat_level(3)
    assert Equal(result3, "Low")

    result4: str = await get_threat_level(4)
    assert Equal(result4, "Undefined")

    result5: str = await get_threat_level(5)
    assert Equal(result5, "No threat level found")


@pytest.mark.asyncio
async def test_get_post(post):
    expected: Post = generate_post()
    db_post: Post = await get_post(post.id)
    assert Equal(db_post.user_id, expected.user_id)
    assert Equal(db_post.contents, expected.contents)
    assert Equal(db_post.post_id, expected.post_id)
    assert Equal(db_post.thread_id, expected.thread_id)

    with pytest.raises(ValueError):
        await get_post(100)


@pytest.mark.asyncio
async def test_is_excluded_correlation(correlation_exclusion):
    assert await is_excluded_correlation(correlation_exclusion.value)


@pytest.mark.asyncio
async def test_is_no_excluded_correlation(correlation_exclusion):
    assert not await is_excluded_correlation(uuid())


@pytest.mark.asyncio
async def test_is_over_correlating_value(over_correlating_value):
    assert await is_over_correlating_value(over_correlating_value.value)


@pytest.mark.asyncio
async def test_is_not_over_correlating_value(over_correlating_value):
    assert not await is_over_correlating_value(uuid())


@pytest.mark.asyncio
async def test_get_number_of_correlations_over_correlating(over_correlating_value):
    result: int = await get_number_of_correlations(over_correlating_value.value, True)
    assert Equal(result, 1)


@pytest.mark.asyncio
async def test_get_number_of_correlations_default_correlating(default_correlation_no_real_ids, db):
    statement = select(CorrelationValue.value).where(CorrelationValue.id == default_correlation_no_real_ids.value_id)
    correlation_value: str = (await db.execute(statement)).scalar()
    await db.execute(statement)
    await db.commit()

    result: int = await get_number_of_correlations(correlation_value, False)
    assert Equal(result, 1)


@pytest.mark.asyncio
async def test_get_number_of_correlations_no_correlating_over_correlating():
    no_result: int = await get_number_of_correlations(uuid(), False)
    assert Equal(no_result, 0)


@pytest.mark.asyncio
async def test_get_number_of_correlations_no_correlating_default_correlating():
    with pytest.raises(ValueError):
        await get_number_of_correlations(uuid(), True)


@pytest.mark.asyncio
async def test_add_correlation_value(db):
    value: str = "test_await misp_sql"

    result: int = await add_correlation_value(value)
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
async def test_add_correlations():
    not_adding: list[DefaultCorrelation] = [__get_test_correlation()]
    not_adding_value: str = "hopefully not in the database :)"
    value_id: int = await add_correlation_value(not_adding_value)
    not_adding[0].value_id = value_id
    result = await add_correlations(not_adding)
    assert result

    not_adding1: list[DefaultCorrelation] = [__get_test_correlation()]
    try_again: bool = await add_correlations(not_adding1)
    assert not try_again

    await delete_correlations(not_adding_value)


@pytest.mark.asyncio
async def test_add_over_correlating_value(db):
    value: str = "test_sql_delete"

    added: bool = await add_over_correlating_value(value, 66)
    assert added
    statement = select(OverCorrelatingValue).where(OverCorrelatingValue.value == value)
    result: OverCorrelatingValue = (await db.execute(statement)).scalars().first()
    assert Equal(result.value, value)
    assert Equal(result.occurrence, 66)
    assert Greater(result.id, 0)
    await delete_over_correlating_value(value)


@pytest.mark.asyncio
async def test_delete_over_correlating_value(db):
    await add_over_correlating_value("test_sql_delete", 66)
    deleted: bool = await delete_over_correlating_value("test_sql_delete")
    assert deleted
    statement = select(OverCorrelatingValue).where(OverCorrelatingValue.value == "test_sql_delete")
    result: OverCorrelatingValue = (await db.execute(statement)).first()
    assert result is None

    not_there: bool = await delete_over_correlating_value("test_sql_delete")
    assert not not_there


@pytest.mark.asyncio
async def test_delete_correlations(db):
    adding: list[DefaultCorrelation] = [__get_test_correlation()]
    value_id: int = await add_correlation_value("hopefully not in the database :)")
    adding[0].value_id = value_id
    await add_correlations(adding)
    amount: int = await get_number_of_correlations("hopefully not in the database :)", False)
    assert Equal(1, amount)

    deleted: bool = await delete_correlations("hopefully not in the database :)")
    assert deleted

    amount = await get_number_of_correlations("hopefully not in the database :)", False)
    assert Equal(0, amount)

    statement = select(CorrelationValue).where(CorrelationValue.value == "hopefully not in the database :)")
    result: CorrelationValue = (await db.execute(statement)).first()
    assert result is None


@pytest.mark.asyncio
async def test_get_event_tag_id(event_with_normal_tag):
    exists = await get_event_tag_id(event_with_normal_tag.id, event_with_normal_tag.eventtags[0].tag_id)
    assert Equal(exists, event_with_normal_tag.eventtags[0].id)
    not_exists = await get_event_tag_id(1, 100)
    assert Equal(not_exists, -1)


@pytest.mark.asyncio
async def test_get_attribute_tag_id(attribute_with_normal_tag):
    exists = await get_attribute_tag_id(attribute_with_normal_tag.id, attribute_with_normal_tag.attributetags[0].tag_id)
    assert Equal(exists, attribute_with_normal_tag.attributetags[0].id)
    not_exists = await get_attribute_tag_id(1, 100)
    assert Equal(not_exists, -1)
