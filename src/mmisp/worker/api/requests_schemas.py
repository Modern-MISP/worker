"""
Encapsulates input data classes for the jobs router.
"""

from enum import StrEnum

from pydantic import BaseModel


class UserData(BaseModel):
    """
    Data class for user_id
    """

    user_id: int
    """The id of the user"""


class JobEnum(StrEnum):
    """
    Represents the implemented jobs
    """

    PULL = "pull"
    PUSH = "push"
    CORRELATE = "correlation"
    ENRICHMENT = "enrichment"
    SEND_EMAIL = "sendEmail"
    PROCESS_FREE_TEXT = "processFreeText"
    IMPORT_TAXONOMIES = "importTaxonomies"
    IMPORT_OBJECT_TEMPLATES = "importObjectTemplates"
    IMPORT_GALAXIES = "galaxy"
    DEBUG = "debug"
