from uuid import UUID

from mmisp.api_schemas.objects import ObjectWithAttributesResponse
from mmisp.db.models.attribute import Attribute
from mmisp.db.models.correlation import Correlation
from mmisp.worker.jobs.correlation.correlation_worker import correlation_worker
from mmisp.api_schemas.events import AddEditGetEventDetails


def save_correlations(attributes: list[Attribute], value: str) -> set[UUID]:
    """
    Method to generate Correlation objects from the given list of MispEventAttribute and save them in the database.
    All MispEventAttribute in the list have to be attributes which have the same value and are correlated with each
    other.
    :param attributes: the attributes to correlate with each other
    :type attributes: list[Attribute]
    :param value: on which the correlations are based
    :type value: str
    :return: a set of UUIDs representing the events the correlation are associated with
    :rtype: set[UUID]
    """
    value_id: int = correlation_worker.misp_sql.add_correlation_value(value)
    events: list[AddEditGetEventDetails] = list()
    objects: list[ObjectWithAttributesResponse] = list()
    for attribute in attributes:
        events.append(correlation_worker.misp_api.get_event(attribute.event_id))
        objects.append(correlation_worker.misp_api.get_object(attribute.object_id))
    correlations = __create_correlations(attributes, events, objects, value_id)
    correlation_worker.misp_sql.add_correlations(correlations)
    result: list[UUID] = list()
    for event in events:
        result.append(event.uuid)
    uuid_set: set[UUID] = set(result)
    return uuid_set


def __create_correlations(attributes: list[Attribute], events: list[AddEditGetEventDetails], objects: list[ObjectWithAttributesResponse],
                          value_id: int) -> list[Correlation]:
    """
    Method to create Correlation objects based on the given list of MispEventAttribute und list of AddEditGetEventDetails.
    For every attribute a correlation is created with any other attribute in the list (except itself).
    The MispEventAttribute at place i in the list has to be an attribute of the AddEditGetEventDetails at place i in the list of
    AddEditGetEventDetails to function properly.

    :param attributes: list of MispEventAttribute to create correlations from
    :param events: list of the MispEvents the MispEventAttribute occurs in
    :param value_id: the id of the value for the correlation
    :return: a list of Correlation
    """
    count: int = len(attributes)
    correlations: list[Correlation] = list()
    for i in range(count):
        for j in range(i + 1, count):
            if attributes[i].event_id != attributes[j].event_id:
                new_correlation: Correlation = _create_correlation_from_attributes(attributes[i],
                                                                                   events[i],
                                                                                   objects[i],
                                                                                   attributes[j],
                                                                                   events[j],
                                                                                   objects[j],
                                                                                   value_id)
                correlations.append(new_correlation)
    return correlations


def _create_correlation_from_attributes(attribute_1: Attribute, event_1: AddEditGetEventDetails,
                                        object_1: ObjectWithAttributesResponse,
                                        attribute_2: Attribute, event_2: AddEditGetEventDetails,
                                        object_2: ObjectWithAttributesResponse,
                                        value_id: int) -> Correlation:
    """
    Method to construct a Correlation object based on two attributes and the events they occur in.
    The value of the correlation is specified by the value id.

    :param attribute_1: first attribute of the correlation
    :type attribute_1: Attribute
    :param event_1: event of the first attribute
    :type event_1: AddEditGetEventDetails
    :param object_1: object of the first attribute
    :type object_1: MispObject
    :param attribute_2: second attribute of the correlation
    :type attribute_2: Attribute
    :param event_2: event of the second attribute
    :type event_2: AddEditGetEventDetails
    :param object_2: object of the second attribute
    :type object_2: MispObject
    :param value_id: value of the correlation
    :type value_id: int
    :return: a Correlation object based on the input
    :rtype: Correlation
    """
    return Correlation(attribute_id=attribute_1.id,
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


def get_amount_of_possible_correlations(attributes: list[Attribute]) -> int:
    """
    Method to calculate the amount of possible correlations for the given list of Attribute.
    The amount of possible correlations is the amount of attributes minus the amount of attributes which are in the same
    event.
    :param attributes: the attributes to calculate the amount of possible correlations for
    :type attributes: list[Attribute]
    :return: the amount of possible correlations
    :rtype: int
    """
    count: int = 0
    for i in range(len(attributes)):
        for j in range(i + 1, len(attributes)):
            if attributes[i].event_id != attributes[j].event_id:
                count += 1
    return count
