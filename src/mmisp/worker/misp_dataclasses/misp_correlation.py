from sqlmodel import SQLModel, Field

from sqlalchemy import Column, Index, text
from sqlalchemy.dialects.mysql import INTEGER, TINYINT
from sqlmodel import SQLModel, Field

from mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_object import MispObject


class MispCorrelation(SQLModel, table=True):
    """
    Dataclass to encapsulate an entry from the "default_correlations"
    table in the misp database.
    """
    __tablename__ = 'default_correlations'
    __table_args__ = (
        Index('unique_correlation', 'attribute_id', '1_attribute_id', 'value_id', unique=True),
    )

    id: int = Field(INTEGER(10), primary_key=True)
    attribute_id: int = Column(INTEGER(10), nullable=False, index=True)
    object_id: int = Column(INTEGER(10), nullable=False, index=True)
    event_id: int = Column(INTEGER(10), nullable=False, index=True)
    org_id: int = Column(INTEGER(10), nullable=False)
    distribution: int = Column(TINYINT(4), nullable=False)
    object_distribution: int = Column(TINYINT(4), nullable=False)
    event_distribution: int = Column(TINYINT(4), nullable=False)
    sharing_group_id: int = Column(INTEGER(10), nullable=False, server_default=text("0"))
    object_sharing_group_id: int = Column(INTEGER(10), nullable=False, server_default=text("0"))
    event_sharing_group_id: int = Column(INTEGER(10), nullable=False, server_default=text("0"))
    _1_attribute_id: int = Column('1_attribute_id', INTEGER(10), nullable=False, index=True)
    _1_object_id: int = Column('1_object_id', INTEGER(10), nullable=False, index=True)
    _1_event_id: int = Column('1_event_id', INTEGER(10), nullable=False, index=True)
    _1_org_id: int = Column('1_org_id', INTEGER(10), nullable=False)
    _1_distribution: int = Column('1_distribution', TINYINT(4), nullable=False)
    _1_object_distribution: int = Column('1_object_distribution', TINYINT(4), nullable=False)
    _1_event_distribution: int = Column('1_event_distribution', TINYINT(4), nullable=False)
    _1_sharing_group_id: int = Column('1_sharing_group_id', INTEGER(10), nullable=False, server_default=text("0"))
    _1_object_sharing_group_id: int = Column('1_object_sharing_group_id', INTEGER(10), nullable=False,
                                             server_default=text("0"))
    _1_event_sharing_group_id: int = Column('1_event_sharing_group_id', INTEGER(10), nullable=False,
                                            server_default=text("0"))
    value_id: int = Column(INTEGER(10), nullable=False, index=True)

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
                   _1_attribute_id=attribute_2.id,
                   _1_object_id=attribute_2.object_id,
                   _1_event_id=attribute_2.event_id,
                   _1_org_id=event_2.org_id,
                   _1_distribution=attribute_2.distribution,
                   _1_object_distribution=object_2.distribution,
                   _1_event_distribution=event_2.distribution,
                   _1_sharing_group_id=attribute_2.sharing_group_id,
                   _1_object_sharing_group_id=object_2.sharing_group_id,
                   _1_event_sharing_group_id=event_2.sharing_group_id,
                   value_id=value_id)
