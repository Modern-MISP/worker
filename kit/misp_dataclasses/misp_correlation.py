
from pydantic import BaseModel


class MispCorrelation(BaseModel):
    """
    Dataclass to encapsulate an entry form the "default_correlations"
    table in the misp database.
    """
    id: int
    attribute_id: int
    object_id: int
    event_id: int
    org_id: int
    distribution: int
    object_distribution: int
    event_distribution: int
    sharing_group_id: int
    object_sharing_group_id: int
    event_sharing_group_id: int
    # Variable name in Misp database without the underscore in front of 1
    _1_attribute_id: int
    _1_object_id: int
    _1_event_id: int
    _1_org_id: int
    _1_distribution: int
    _1_object_distribution: int
    _1_event_distribution: int
    _1_sharing_group_id: int
    _1_object_sharing_group_id: int
    _1_event_sharing_group_id: int
    value_id: int
