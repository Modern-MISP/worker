from enum import Enum

from pydantic import BaseModel


class PullTechniqueEnum(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    PULL_RELEVANT_CLUSTERS = "pull_relevant_clusters"


class PullData(BaseModel):
    server_id: int
    technique: PullTechniqueEnum


class PullResult(BaseModel):
    successes: int
    fails: int
    pulled_proposals: int
    pulled_sightings: int
    pulled_clusters: int

