from uuid import UUID

from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.jobs.correlation.job_data import CorrelateValueResponse, CorrelateValueData
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute
from mmisp.worker.jobs.correlation.correlation_worker import CorrelationWorker, correlation_worker
from mmisp.worker.misp_dataclasses.misp_correlation import MispCorrelation
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_object import MispObject


@celery_app.task
def correlate_value_job(correlate_value_data: CorrelateValueData) -> CorrelateValueResponse:
    """
    Method to execute the job. In CorrelateValueData is the value to correlate.

    :param correlate_value_data: value to correlate
    :type correlate_value_data: CorrelateValue
    :return: relevant information about the correlation
    :rtype: CorrelateValueResponse
    """
    return correlate_value(correlation_worker.misp_sql, correlation_worker.misp_api, correlate_value_data.value)


def correlate_value(misp_sql: MispSQL, misp_api: MispAPI, value: str) -> CorrelateValueResponse:
    """
    Static method to correlate the given value based on the misp_sql database and misp_api interface.
    :param misp_sql: the misp sql database to get information from and store results
    :type misp_sql: MispSQL
    :param misp_api: the misp api to get information from the misp instance
    :type misp_api: MispAPI
    :param value: to correlate
    :param value: string
    :return: relevant information about the correlation
    :rtype: CorrelateValueResponse
    """
    # TODO exceptions
    if misp_sql.is_excluded_correlation(value):
        return CorrelateValueResponse(success=True, found_correlations=False, is_excluded_value=True,
                                      is_over_correlating_value=False, plugin_name=None, events=None)
    attributes: list[MispEventAttribute] = misp_sql.get_attributes_with_correlations(value)
    count: int = len(attributes)
    if count > CorrelationWorker.get_threshold():
        misp_sql.add_over_correlating_value(value, count)
        return CorrelateValueResponse(success=True, found_correlations=True, is_excluded_value=False,
                                      is_over_correlating_value=True, plugin_name=None, events=None)
    elif count > 1:
        value_id: int = misp_sql.add_correlation_value(value)
        events: list[MispEvent] = list()
        objects: list[MispObject] = list()
        for attribute in attributes:
            events.append(misp_api.get_event(attribute.event_id))
            objects.append(misp_api.get_object(attribute.object_id))
        correlations = __create_correlations(attributes, events, objects, value_id)
        misp_sql.add_correlations(correlations)
        uuids: list[UUID] = __get_uuids_from_events(events)
        return CorrelateValueResponse(success=True, found_correlations=True, is_excluded_value=False,
                                      is_over_correlating_value=False, plugin_name=None, events=uuids)
    else:
        return CorrelateValueResponse(success=True, found_correlations=False, is_excluded_value=False,
                                      is_over_correlating_value=False, plugin_name=None, events=None)


def __create_correlations(attributes: list[MispEventAttribute], events: list[MispEvent], objects: list[MispObject],
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


def __get_uuids_from_events(events: list[MispEvent]) -> list[UUID]:
    """
    Method to extract a list of UUIDs from a given list of MispEvent.
    :param events: list of MispEvent to get the UUIDs from
    :return: list of UUIDs
    """
    result: list[UUID] = list()
    for event in events:
        result.append(event.uuid)
    return result
