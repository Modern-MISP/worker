from pydantic import BaseModel

class AttributeType(BaseModel):
    types: list[str]
    default_type: str
    value: str
