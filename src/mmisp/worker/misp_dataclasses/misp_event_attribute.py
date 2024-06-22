from mmisp.api_schemas.attributes import GetAttributeAttributes, GetAttributeTag
from mmisp.worker.misp_dataclasses.attribute_tag_relationship import AttributeTagRelationship


class MispFullAttribute(GetAttributeAttributes):
    """
    Encapsulates a full MISP Attribute with all it's tags and tag relationships.
    """

    attribute_tags: list[tuple[GetAttributeTag, AttributeTagRelationship]] = []
    """A list of tags with it's relationships attached to the attribute."""
