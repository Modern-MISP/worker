import pytest_asyncio

from mmisp.db.models.attribute import Attribute
from mmisp.db.models.event import Event
from mmisp.tests.generators.model_generators.attribute_generator import generate_text_attribute

from .fixtures import CORRELATION_VALUE


@pytest_asyncio.fixture
async def correlation_test_event(db, event) -> Event:
    attributes: list[Attribute] = []

    for i in range(2):
        attribute: Attribute = generate_text_attribute(event.id, CORRELATION_VALUE)
        db.add(attribute)
        await db.commit()
        await db.refresh(attribute)
        attributes.append(attribute)

    await db.refresh(event)
    yield event

    for attribute in attributes:
        await db.delete(attribute)
    await db.commit()
    await db.refresh(event)


@pytest_asyncio.fixture
async def correlation_test_event_2(db, event2) -> Event:
    attributes: list[Attribute] = []

    for i in range(2):
        attribute: Attribute = generate_text_attribute(event2.id, CORRELATION_VALUE)
        db.add(attribute)
        await db.commit()
        await db.refresh(attribute)
        attributes.append(attribute)

    await db.refresh(event2)
    yield event2

    for attribute in attributes:
        await db.delete(attribute)
    await db.commit()
    await db.refresh(event2)
