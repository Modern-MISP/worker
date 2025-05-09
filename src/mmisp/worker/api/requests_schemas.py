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
    SEND_EMAIL = "email"
    PROCESS_FREE_TEXT = "processfreetext"
    IMPORT_TAXONOMIES = "taxonomy"
    IMPORT_OBJECT_TEMPLATES = "object_template"
    IMPORT_GALAXIES = "galaxy"
    IMPORT_FEED = "importFeed"
    DEBUG = "debug"
