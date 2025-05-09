from collections.abc import Iterable
from time import sleep
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.api_schemas.attributes import AddAttributeBody
from mmisp.db.models.attribute import Attribute
from mmisp.lib.distribution import AttributeDistributionLevels
from mmisp.plugins import factory
from mmisp.plugins.enrichment.data import EnrichAttributeResult
from mmisp.plugins.types import EnrichmentPluginType, PluginType

EXAMPLE_ATTRIBUTE: AddAttributeBody = AddAttributeBody(
    event_id=1,
    object_id=0,
    category="Other",
    type="other",
    distribution=AttributeDistributionLevels.OWN_ORGANIZATION,
    value="Test",
)


class BlockingPlugin:
    NAME: str = "Blocking Plugin"
    PLUGIN_TYPE: PluginType = PluginType.ENRICHMENT
    DESCRIPTION: str = "The plugin blocks the job for a certain amount of time without doing anything else."
    AUTHOR: str = "Amadeus Haessler"
    VERSION: str = "1.0"
    ENRICHMENT_TYPE: Iterable[EnrichmentPluginType] = frozenset(
        {EnrichmentPluginType.EXPANSION, EnrichmentPluginType.HOVER}
    )
    ATTRIBUTE_TYPES_INPUT = ["other"]
    ATTRIBUTE_TYPES_OUTPUT = ["other"]

    async def run(self: Self, db: AsyncSession, attribute: Attribute) -> EnrichAttributeResult:
        sleep(5)
        return EnrichAttributeResult()


factory.register(BlockingPlugin())
