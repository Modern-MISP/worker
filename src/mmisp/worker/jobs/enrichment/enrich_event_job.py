from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.jobs.enrichment.job_data import EnrichEventData, EnrichEventResult

"""
Encapsulates a Job enriching a given MISP Event.

Job fetches MISP Attributes from a given Event and executes the specified enrichment plugins
for each of these attributes.
Newly created Attributes and Tags are attached to the Event directly in the MISP-Database.
"""


@celery_app.task
def enrich_event_job(data: EnrichEventData) -> EnrichEventResult:
    """
    Runs the enrichment process.

    Executes each plugin for each attribute of the given event.
    The created attributes and tags are attached to the event.
    :param data: The event id and enrichment plugins.
    :return: The number of newly created attributes.
    :rtype: EnrichEventResult
    """

    # 1. Fetch Attributes by event id
    # 2. Initialize Plugins
    # 3. Run Plugins
    # 4. Write created attributes and tags to database
    pass
