from collections.abc import Iterable
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.db.models.attribute import Attribute
from mmisp.plugins import factory
from mmisp.plugins.enrichment.data import EnrichAttributeResult
from mmisp.plugins.types import EnrichmentPluginType, PluginType


class DummyPlugin:
    NAME: str = "Dummy Plugin"
    PLUGIN_TYPE: PluginType = PluginType.ENRICHMENT
    DESCRIPTION: str = "This is a useless Plugin for demonstration purposes."
    AUTHOR: str = "Amadeus Haessler"
    VERSION: str = "1.0"
    ENRICHMENT_TYPE: Iterable[EnrichmentPluginType] = frozenset(
        {EnrichmentPluginType.EXPANSION, EnrichmentPluginType.HOVER}
    )
    ATTRIBUTE_TYPES_INPUT = ["hostname", "domain"]
    ATTRIBUTE_TYPES_OUTPUT = ["ip-src", "ip-dst"]

    async def run(self: Self, db: AsyncSession, attribute: Attribute) -> EnrichAttributeResult:
        # Plugin logic is implemented here.
        ...


factory.register(DummyPlugin())
