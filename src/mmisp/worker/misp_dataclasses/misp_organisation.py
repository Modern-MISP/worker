from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, field_validator


class MispOrganisation(BaseModel):
    """
    Encapsulates a MISP Organisation.
    """
    id: int
    name: str
    date_created: datetime | None = None
    date_modified: datetime | None = None
    description: str | None = None
    type: str | None = None
    nationality: str | None = None
    sector: str | None = None
    created_by: int | None = None
    uuid: str | None = None
    contacts: str | None = None
    local: bool | None = None
    restricted_to_domain: list[str] | None = None
    landing_page: str | None = None
    user_count: int | None = None
    created_by_email: str | None = None

    @field_validator('*', mode='before')
    @classmethod
    def empty_str_to_none(cls, value: Any) -> Any:
        """
        Convert empty strings to None.

        :param value: value to convert
        :type value: Any
        :return: returns the value if it is not an empty string, otherwise None
        :rtype: Any
        """
        if value == "":
            return None

        return value


    @field_validator('restricted_to_domain', mode='before')
    @classmethod
    def empty_list_to_list(cls, value: Any) -> Any:
        """
        Convert empty list-string to empty list.

        :param value: value to convert
        :type value: Any
        :return: returns the value if it is not an empty list, otherwise None
        :rtype: Any
        """
        if value == "[]":
            return []

        return value