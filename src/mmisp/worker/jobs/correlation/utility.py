from uuid import UUID

from mmisp.worker.jobs.correlation.correlation_worker import correlation_worker
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispSQLEventAttribute
from mmisp.worker.misp_dataclasses.misp_correlation import MispCorrelation
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_object import MispObject


def save_correlations(attributes: list[MispSQLEventAttribute], value: str) -> set[UUID]:
    """
    Method to generate MispCorrelation objects from the given list of MispEventAttribute and save them in the database.
    All MispEventAttribute in the list have to be attributes which have the same value and are correlated with each
    other.
    :param attributes: the attributes to correlate with each other
    :type attributes: list[MispSQLEventAttribute]
    :param value: on which the correlations are based
    :type value: str
    :return: a set of UUIDs representing the events the correlation are associated with
    :rtype: set[UUID]
    """
    value_id: int = correlation_worker.misp_sql.add_correlation_value(value)
    events: list[MispEvent] = list()
    objects: list[MispObject] = list()
    for attribute in attributes:
        events.append(correlation_worker.misp_api.get_event(attribute.event_id))
        objects.append(correlation_worker.misp_api.get_object(attribute.object_id))
    correlations = __create_correlations(attributes, events, objects, value_id)
    correlation_worker.misp_sql.add_correlations(correlations)
    uuids: list[UUID] = MispEvent.get_uuids_from_events(events)
    uuid_set: set[UUID] = set(uuids)
    return uuid_set


def __create_correlations(attributes: list[MispSQLEventAttribute], events: list[MispEvent], objects: list[MispObject],
                          value_id: int) -> list[MispCorrelation]:
    """
    Method to create MispCorrelation objects based on the given list of MispEventAttribute und list of MispEvent.
    For every attribute a correlation is created with any other attribute in the list (except itself).
    The MispEventAttribute at place i in the list has to be an attribute of the MispEvent at place i in the list of
    MispEvent to function properly.

    :param attributes: list of MispEventAttribute to create correlations from
    :param events: list of the MispEvents the MispEventAttribute occurs in
    :param value_id: the id of the value for the correlation
    :return: a list of MispCorrelation
    """
    count: int = len(attributes)
    correlations: list[MispCorrelation] = list()
    for i in range(count):
        for j in range(i + 1, count):
            if attributes[i].event_id != attributes[j].event_id:
                new_correlation: MispCorrelation = MispCorrelation.create_from_attributes(attributes[i],
                                                                                          events[i],
                                                                                          objects[i],
                                                                                          attributes[j],
                                                                                          events[j],
                                                                                          objects[j],
                                                                                          value_id)
                correlations.append(new_correlation)
    return correlations


def get_amount_of_possible_correlations(attributes: list[MispSQLEventAttribute]) -> int:
    """
    Method to calculate the amount of possible correlations for the given list of MispSQLEventAttribute.
    The amount of possible correlations is the amount of attributes minus the amount of attributes which are in the same
    event.
    :param attributes: the attributes to calculate the amount of possible correlations for
    :type attributes: list[MispSQLEventAttribute]
    :return: the amount of possible correlations
    :rtype: int
    """
    count: int = 0
    for i in range(len(attributes)):
        for j in range(i + 1, len(attributes)):
            if attributes[i].event_id != attributes[j].event_id:
                count += 1
    return count
