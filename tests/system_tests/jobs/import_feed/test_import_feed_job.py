import pytest
from sqlalchemy.future import select
from sqlalchemy.orm import Session, selectinload
from src.mmisp.worker.api.requests_schemas import UserData
from src.mmisp.worker.jobs.import_feed.job_data import ImportFeedData

from mmisp.db.models.event import Event
from mmisp.db.models.feed import Feed
from mmisp.worker.jobs.import_feed.import_feed_job import _import_feed_job
from mmisp.db.models.event import Event
from sqlalchemy.orm import selectinload

@pytest.mark.asyncio
async def test_import_feed_job_misp(
    db: Session,
) -> None:
    feed = Feed(
        url="https://www.circl.lu/doc/misp/feed-osint/",
        source_format="misp",
        name="Test Feed",
        provider="tester",
        settings="assdfsdfd",
    )
    user = UserData(user_id=228)
    db.add(feed)
    await db.commit()
    await db.refresh(feed)
    data = ImportFeedData(id=feed.id)
    result = await _import_feed_job(user, data)
    assert result.success is True
    feed_event = await db.scalar(select(Event).where(Event.uuid == "0b988513-9535-42f0-9ebc-5d6aec2e1c79"))
    assert feed_event is not None
    assert feed_event.analysis == "2"
    assert feed_event.date == "2020-11-27"
    assert feed_event.extends_uuid == ""
    assert feed_event.info == "OSINT - Egregor: The New Ransomware Variant To Watch"
    assert feed_event.publish_timestamp == "1607324084"
    assert feed_event.published is True
    assert feed_event.threat_level_id == "1"
    assert feed_event.timestamp == "1607324075"
    assert feed_event.uuid == "0b988513-9535-42f0-9ebc-5d6aec2e1c79"

@pytest.mark.asyncio
async def test_import_feed_job_misp_wrong_link_format(
        db: Session,
) -> None:
    feed = Feed(
        url="https://www.circl.lu/doc/misp/feed-osin",
        source_format="misp",
        name="Test Feed",
        provider="tester",
        settings="assdfsdfd",
    )
    user = UserData(user_id=228)
    db.add(feed)
    await db.commit()
    await db.refresh(feed)
    data = ImportFeedData(id=feed.id)
    await _import_feed_job(user, data)
@pytest.mark.asyncio
async def test_import_feed_job_csv_wrong_link_format(
        db: Session,
) -> None:
    feed = Feed(
        url="https://blocklist.greensnow.co/gre",
        source_format="csv",
        name="Test Feed",
        provider="tester",
        settings="assdfsdfd",
    )
    user = UserData(user_id=228)
    db.add(feed)
    await db.commit()
    await db.refresh(feed)
    data = ImportFeedData(id=feed.id)
    await _import_feed_job(user, data)
@pytest.mark.asyncio
async def test_import_feed_job_feed_none() -> None:
    user = UserData(user_id=228)
    data = ImportFeedData(id=409321492394343)
    result = await _import_feed_job(user, data)
    assert result.success is False
    assert result.message == "no such feed found"
@pytest.mark.asyncio
async def test_import_feed_job_csv(
    db: Session,
) -> None:
    feed = Feed(
        url="https://blocklist.greensnow.co/greensnow.txt",
        source_format="csv",
        name="Test Feed",
        provider="tester",
        settings="assdfsdfd",
    )
    user = UserData(user_id=228)
    db.add(feed)
    await db.commit()
    await db.refresh(feed)
    data = ImportFeedData(id=feed.id)
    result = await _import_feed_job(user, data)
    assert result.success is True
    feed_event = await db.execute(
        select(Event).where(Event.info == feed.name).options(selectinload(Event.attributes))
    )
    assert feed_event is not None
    for attr in feed_event.attributes:
        assert (attr.type == "ip-dst" or attr.type == "ip-src" or attr.type == "ip-src/ip-dst")
        assert attr.category == "Network activity"
@pytest.mark.asyncio
async def test_import_feed_job_csv_fixed_event(
        db: Session,
) -> None:
    feed = Feed(
        url="https://blocklist.greensnow.co/greensnow.txt",
        source_format="csv",
        name="Test Feed",
        provider="tester",
        settings="assdfsdfd",
    )
    user = UserData(user_id=228)
    db.add(feed)
    await db.commit()
    await db.refresh(feed)
    data = ImportFeedData(id=feed.id)
    result = await _import_feed_job(user, data)
    assert result.success is True
