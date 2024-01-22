from src.mmisp.worker.job.enrichment_job.job_data import EnrichEventData, EnrichEventResult
#from src.mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute
#from src.mmisp.worker.misp_dataclasses.misp_tag import MispTag
from src.mmisp.worker.job.job import Job
#from src.mmisp.worker.misp_database.misp_api import MispAPI
#from src.mmisp.worker.job.enrichment_job.plugins.enrichment_plugin import EnrichmentPlugin, EnrichmentPluginType
#from src.mmisp.worker.job.enrichment_job.plugins.enrichment_plugin_factory import EnrichmentPluginFactory
#from mmisp.worker.job.enrichment_job.enrich_attribute_job import EnrichAttributeJob


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
