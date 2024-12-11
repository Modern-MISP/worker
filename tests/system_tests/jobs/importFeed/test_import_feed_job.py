import pytest
from sqlalchemy.orm import Session
from src.mmisp.worker.api.requests_schemas import UserData
from src.mmisp.worker.jobs.importFeed.job_data import ImportFeedData

from mmisp.db.models.feed import Feed
from mmisp.worker.jobs.importFeed.import_feed_job import _import_feed_job


@pytest.mark.asyncio
async def test_import_feed_job_misp(
    db: Session,
) -> None:
    feed = Feed(
        url="https://www.circl.lu/doc/misp/feed-osint/0ebe51c2-31f1-4ba4-b7ab-1f5e62531e45.json",
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
