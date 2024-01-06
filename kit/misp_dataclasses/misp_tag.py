import json
from pydantic import BaseModel

# Needed to generate JSON Representation of dataclasses
from kit.utilities.naming_utils import snake_to_camel_case


class MispTag(BaseModel):
    """
    TODO: Docstring
    TODO: Nochmal auf Vollständigkeit überprüfen.
    TODO: Validierungsmethoden
    """
    id: int
    name: str
    colour: str
    exportable: bool
    org_id: int
    user_id: str
    hide_tag: bool
    numerical_value: int
    is_galaxy: bool
    is_custom_galaxy: bool
    inherited: int

    # Ahmad added these
    local_only: bool
    local: int
    relationship_type: str  # unsure of type

    def to_json(self) -> str:
        pass
