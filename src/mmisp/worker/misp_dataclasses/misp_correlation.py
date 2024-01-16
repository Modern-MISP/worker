
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
    # Variable name in Misp database without the last underscore and 1, but with 1 and underscore in front of the name
    attribute_id_1: int
    object_id_1: int
    event_id_1: int
    org_id_1: int
    distribution_1: int
    object_distribution_1: int
    event_distribution_1: int
    sharing_group_id_1: int
    object_sharing_group_id_1: int
    event_sharing_group_id_1: int
    value_id: int
