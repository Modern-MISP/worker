import pytest
from sqlalchemy.future import select
from sqlalchemy.orm import Session, selectinload
from src.mmisp.worker.api.requests_schemas import UserData
from src.mmisp.worker.jobs.import_feed.job_data import ImportFeedData

from mmisp.db.models.event import Event
from mmisp.db.models.feed import Feed
from mmisp.worker.jobs.import_feed.import_feed_job import _import_feed_job


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
    await _import_feed_job(user, data)
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
async def test_import_feed_job_feed_none() -> None:
    user = UserData(user_id=228)
    data = ImportFeedData(id=409321492394343)
    await _import_feed_job(user, data)
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
    await _import_feed_job(user, data)
