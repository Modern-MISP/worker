from typing import Optional

from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_event import MispEvent


class MispCorrelation(BaseModel):
    """
    Dataclass to encapsulate an entry form the "default_correlations"
    table in the misp database.
    """
    id: Optional[int] = None
    # first attribute
    attribute_id: int
    object_id: int
    event_id: int
    org_id: int
    distribution: int
    object_distribution: int # fehlt noch
    event_distribution: int
    sharing_group_id: int
    object_sharing_group_id: int #fehlt noch
    event_sharing_group_id: int
    # second attribute
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

    @classmethod
    def create_from_attributes(cls, attribute_1: MispEventAttribute, event_1: MispEvent,
                               attribute_2: MispEventAttribute, event_2: MispEvent, value_id: int):
        """
        Method to construct a MispCorrelation object based on two attributes and the events they occur in.
        The value of the correlation is specified by the value id.

        @param attribute_1: first attribute of the correlation
        @param event_1: event of the first attribute
        @param attribute_2: second attribute of the correlation
        @param event_2: event of the second attribute
        @param value_id: value of the correlation
        @return: a MispCorrelation object based on the input
        """
        # TODO add object distribution, sharing group id
        return cls(attribute_id=attribute_1.id, object_id=attribute_1.object_id,
                   event_id=attribute_1.event_id, org_id=event_1.org_id,
                   distribution=attribute_1.distribution, event_distribution=event_1.event_distribution,
                   sharing_group_id=attribute_1.sharing_group_id,
                   event_sharing_group_id=event_1.sharing_group_id, attribute_id_1=attribute_2.id,
                   object_id_1=attribute_2.object_id, event_id_1=attribute_2.event_id,
                   org_id_1=event_2.org_id, distribution_1=attribute_2.distribution,
                   event_distribution_1=event_2.distribution, sharing_group_id_1=attribute_2.sharing_group_id,
                   event_sharing_group_id_1=event_2.sharing_group_id, value_id=value_id)
