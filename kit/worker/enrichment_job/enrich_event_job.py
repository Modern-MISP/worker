from pydantic import BaseModel

from kit.misp_dataclasses.misp_attribute import MispEventAttribute
from kit.misp_dataclasses.misp_tag import MispTag
from kit.worker.job import Job
from kit.misp_database.misp_api import MispAPI
from kit.worker.enrichment_job.plugins.enrichment_plugin import EnrichmentPlugin, EnrichmentPluginType
from kit.worker.enrichment_job.plugins.enrichment_plugin_factory import EnrichmentPluginFactory
from kit.worker.enrichment_job.enrich_attribute_job import EnrichAttributeJob


class EnrichEventData(BaseModel):
    """
    Encapsulates the data needed for an enrich-event job.
    """
    eventId: int
    enrichmentPlugins: list[str]


class EnrichEventResult(BaseModel):
    """
    Encapsulates the result of an enrich-event job.

    Contains the number of created attributes.
    """
    created_attributes: int


class EnrichEventJob(Job):
    """
    Encapsulates a Job enriching a given MISP Event.

    Job fetches MISP Attributes from a given Event and executes the specified enrichment plugins
    for each of these attributes.
    Newly created Attributes and Tags are attached to the Event directly in the MISP-Database.
    """

    def run(self, data: EnrichEventData) -> EnrichEventResult:
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
