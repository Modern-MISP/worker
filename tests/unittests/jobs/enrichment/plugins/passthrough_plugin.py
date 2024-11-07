from typing import Self

from mmisp.api_schemas.attributes import AddAttributeBody
from mmisp.plugins.enrichment.data import EnrichAttributeResult, NewAttribute, NewTag
from mmisp.plugins.enrichment.enrichment_plugin import EnrichmentPluginInfo, EnrichmentPluginType, PluginIO
from mmisp.plugins.models.attribute import AttributeWithTagRelationship
from mmisp.plugins.plugin_type import PluginType


class PassthroughPlugin:
    PLUGIN_INFO: EnrichmentPluginInfo = EnrichmentPluginInfo(
        NAME="Passthrough Plugin",
        PLUGIN_TYPE=PluginType.ENRICHMENT,
        DESCRIPTION="This is a test plugin returning the input unchanged.",
        AUTHOR="Amadeus Haessler",
        VERSION="1.0",
        ENRICHMENT_TYPE={EnrichmentPluginType.EXPANSION},
        MISP_ATTRIBUTES=PluginIO(INPUT=["Any"], OUTPUT=["Any"]),
    )

    def __init__(self: Self, misp_attribute: AttributeWithTagRelationship) -> None:
        self._misp_attribute: AttributeWithTagRelationship = misp_attribute

    def run(self: Self) -> EnrichAttributeResult:
        attribute: AddAttributeBody = AddAttributeBody(**self._misp_attribute.dict())
        tags: list[NewTag] = []

        for tag in self._misp_attribute.Tag:
            tags.append(NewTag(tag_id=tag.id, local=tag.relationship_local, relationship_type=tag.relationship_type))

        return EnrichAttributeResult(attributes=[NewAttribute(attribute=attribute, tags=tags)])
