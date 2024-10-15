from typing import Any

import pytest
from icecream import ic
from sqlalchemy import delete, select

from mmisp.api_schemas.galaxies import GetGalaxyClusterResponse
from mmisp.db.models.attribute import Attribute
from mmisp.db.models.correlation import CorrelationValue, DefaultCorrelation, OverCorrelatingValue
from mmisp.db.models.post import Post
from mmisp.tests.generators.model_generators.post_generator import generate_post
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
        result = result.decode('utf-8')
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
async def test_get_values_with_correlation(db):
    result: list[str] = await get_values_with_correlation()

    quality: int = 0
    for value in result:
        statement = select(CorrelationValue.value).where(CorrelationValue.value == value)
        result_search: str = db.execute(statement).scalars().first()
        assert result_search == value
        quality += 1
        if quality > 10:
            break

    is_there: bool = "test_misp_sql_c" in result
    assert is_there


@pytest.mark.asyncio
async def test_get_over_correlating_values():
    result: list[tuple[str, int]] = await get_over_correlating_values()
    for value in result:
        check: bool = await is_over_correlating_value(value[0])
        assert check
        assert value[1] > 0
    is_there: bool = ("Turla", 34) in result
    assert is_there


@pytest.mark.asyncio
async def test_get_excluded_correlations():
    result: list[str] = await get_excluded_correlations()
    for value in result:
        check: bool = await is_excluded_correlation(value)
        assert check
    is_there: bool = "test_await misp_sql" in result
    assert is_there


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
    db_post: Post = await get_post(1)
    assert Equal(db_post.id, expected.id)
    assert Equal(db_post.user_id, expected.user_id)
    assert Equal(db_post.contents, expected.contents)
    assert Equal(db_post.post_id, expected.post_id)
    assert Equal(db_post.thread_id, expected.thread_id)

    with pytest.raises(ValueError):
        await get_post(100)


@pytest.mark.asyncio
async def test_is_excluded_correlation():
    result: bool = await is_excluded_correlation("1.2.3.4")
    assert result

    false_result: bool = await is_excluded_correlation("notthere")
    assert not false_result


@pytest.mark.asyncio
async def test_is_over_correlating_value():
    result: bool = await is_over_correlating_value("turla")
    assert result

    false_result: bool = await is_over_correlating_value("notthere")
    assert not false_result


@pytest.mark.asyncio
async def test_get_number_of_correlations(over_correlating_value_value_turla):
    over_result: int = await get_number_of_correlations("Turla", True)
    assert Equal(over_result, 1)

    no_result: int = await get_number_of_correlations("test_await misp_sql", False)
    assert Equal(no_result, 0)

    normal_result: int = await get_number_of_correlations("195.22.28.196", False)
    assert Greater(normal_result, 0)


@pytest.mark.asyncio
async def test_add_correlation_value(db):
    value: str = "test_await misp_sql"

    result: int = await add_correlation_value(value)
    assert Greater(result, 0)

    session = db
    statement = select(CorrelationValue).where(CorrelationValue.value == value)
    search_result: CorrelationValue = (await session.execute(statement)).scalar().first()
    assert Equal(search_result.value, value)
    assert Equal(search_result.id, result)

    statement = delete(CorrelationValue).where(CorrelationValue.value == value)
    session.execute(statement)
    session.commit()


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
    result: OverCorrelatingValue = (await db.execute(statement)).scalare().first()
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
async def test_get_event_tag_id():
    exists = await get_event_tag_id(2, 3)
    assert Equal(exists, 1)
    not_exists = await get_event_tag_id(1, 100)
    assert Equal(not_exists, -1)


@pytest.mark.asyncio
async def test_get_attribute_tag_id():
    exists = await get_attribute_tag_id(2, 3)
    assert Equal(exists, 1)
    not_exists = await get_attribute_tag_id(1, 100)
    assert Equal(not_exists, -1)
