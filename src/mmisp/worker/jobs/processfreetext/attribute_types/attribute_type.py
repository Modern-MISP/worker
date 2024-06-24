from pydantic import BaseModel


class AttributeType(BaseModel):
    """
    Encapsulates the attribute type of MISP attribute.
    """

    types: list[str]
    default_type: str
    value: str
