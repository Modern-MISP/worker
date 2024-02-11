from enum import Enum

from pydantic import BaseModel


class PullTechniqueEnum(str, Enum):
    """
    Enum for the different pull techniques.
    """
    FULL = "full"
    INCREMENTAL = "incremental"
    PULL_RELEVANT_CLUSTERS = "pull_relevant_clusters"


class PullData(BaseModel):
    """
    Represents the input data of the PullJob.
    """
    server_id: int
    technique: PullTechniqueEnum


class PullResult(BaseModel):
    """
    Represents the result of a PullJob.
    """
    successes: int
    fails: int
    pulled_proposals: int
    pulled_sightings: int
    pulled_clusters: int


