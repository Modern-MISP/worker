from typing import Optional

from sqlmodel import SQLModel, Field

from mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_object import MispObject


class MispCorrelation(SQLModel):
    """
    Dataclass to encapsulate an entry from the "default_correlations"
    table in the misp database.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    # first attribute
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
    # second attribute
    # variable name in Misp database without the last underscore and 1, but with 1 and underscore in front of the name
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
    def create_from_attributes(cls, attribute_1: MispEventAttribute, event_1: MispEvent, object_1: MispObject,
                               attribute_2: MispEventAttribute, event_2: MispEvent, object_2: MispObject,
                               value_id: int):
        """
        Method to construct a MispCorrelation object based on two attributes and the events they occur in.
        The value of the correlation is specified by the value id.

        :param attribute_1: first attribute of the correlation
        :param event_1: event of the first attribute
        :param object_1: object of the first attribute
        :param attribute_2: second attribute of the correlation
        :param event_2: event of the second attribute
        :param object_2: object of the second attribute
        :param value_id: value of the correlation
        :return: a MispCorrelation object based on the input
        :rtype: MispCorrelation
        """
        return cls(attribute_id=attribute_1.id,
                   object_id=attribute_1.object_id,
                   event_id=attribute_1.event_id,
                   org_id=event_1.org_id,
                   distribution=attribute_1.distribution,
                   object_distribution=object_1.distribution,
                   event_distribution=event_1.distribution,
                   sharing_group_id=attribute_1.sharing_group_id,
                   object_sharing_group_id=object_1.sharing_group_id,
                   event_sharing_group_id=event_1.sharing_group_id,
                   attribute_id_1=attribute_2.id,
                   object_id_1=attribute_2.object_id,
                   event_id_1=attribute_2.event_id,
                   org_id_1=event_2.org_id,
                   distribution_1=attribute_2.distribution,
                   object_distribution_1=object_2.distribution,
                   event_distribution_1=event_2.distribution,
                   sharing_group_id_1=attribute_2.sharing_group_id,
                   object_sharing_group_id_1=object_2.sharing_group_id,
                   event_sharing_group_id_1=event_2.sharing_group_id,
                   value_id=value_id)
