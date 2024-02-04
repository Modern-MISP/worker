from uuid import UUID

from mmisp.worker.controller.celery_app.celery_app import celery_app
from mmisp.worker.jobs.correlation.correlation_worker import correlation_worker
from mmisp.worker.jobs.correlation.job_data import CorrelateValueResponse, CorrelateValueData
from mmisp.worker.jobs.correlation.utility import save_correlations
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispEventAttribute


@celery_app.task
def correlate_value_job(correlate_value_data: CorrelateValueData) -> CorrelateValueResponse:
    """
    Method to execute the job. In CorrelateValueData is the value to correlate.

    :param correlate_value_data: value to correlate
    :type correlate_value_data: CorrelateValue
    :return: relevant information about the correlation
    :rtype: CorrelateValueResponse
    """
    return correlate_value(correlate_value_data.value)


def correlate_value(value: str) -> CorrelateValueResponse:
    """
    Static method to correlate the given value based on the misp_sql database and misp_api interface.
    :param value: to correlate
    :param value: string
    :return: relevant information about the correlation
    :rtype: CorrelateValueResponse
    """
    # TODO exceptions
    if correlation_worker.misp_sql.is_excluded_correlation(value):
        return CorrelateValueResponse(success=True, found_correlations=False, is_excluded_value=True,
                                      is_over_correlating_value=False, plugin_name=None, events=None)
    attributes: list[MispEventAttribute] = correlation_worker.misp_sql.get_attributes_with_same_value(value)
    count: int = len(attributes)
    if count > correlation_worker.threshold():
        correlation_worker.misp_sql.add_over_correlating_value(value, count)
        return CorrelateValueResponse(success=True, found_correlations=True, is_excluded_value=False,
                                      is_over_correlating_value=True, plugin_name=None, events=None)
    elif count > 1:
        uuid_events: set[UUID] = save_correlations(attributes, value)
        return CorrelateValueResponse(success=True, found_correlations=True, is_excluded_value=False,
                                      is_over_correlating_value=False, plugin_name=None, events=uuid_events)
    else:
        return CorrelateValueResponse(success=True, found_correlations=False, is_excluded_value=False,
                                      is_over_correlating_value=False, plugin_name=None, events=None)


