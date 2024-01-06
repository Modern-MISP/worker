from typing import List

from kit.misp_dataclasses.misp_attribute import EventAttribute
from kit.misp_dataclasses.misp_tag import Tag
from kit.worker.worker import Worker
from kit.misp_database.misp_api import MispAPI
from kit.misp_database.misp_sql import MispSQL
from kit.worker.enrichment_worker.plugins.enrichment_plugin import EnrichmentPlugin, EnrichmentPluginType
from kit.worker.enrichment_worker.plugins.enrichment_plugin_factory import EnrichmentPluginFactory
from kit.worker.enrichment_worker.enrich_attribute_job import EnrichAttributeJob


class EnrichEventJob(Worker):
    """
    Encapsulates a Job enriching a given Event.

    Job obtains MISP Attributes from a given Event and runs the specified enrichment plugins for each of those.
    Newly created Attributes and Tags are attached to the Event directly in the MISP-Database.
    """

    def run(self, event_id: int, enrichment_plugins: List[str]) -> int:
        """

        :param event_id: The ID of the MISP Event.
        :type event_id: int
        :param enrichment_plugins: List of available enrichment Plugins to enrich then event with.
        :type enrichment_plugins: List[str]

        :return: The created job object.
        :rtype: EnrichEventJob
        """

        # 1. Fetch Attributes by event id
        # 2. Initialize Plugins
        # 3. Run Plugins
        # 4. Write created attributes and tags to database
        pass
