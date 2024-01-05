from kit.worker.enrich_worker.plugins.enrich_plugin_factory import EnrichPluginFactory
from kit.worker.worker import Worker


class EnrichWorker(Worker):

    def __init__(self):
        self.plugin_factory = EnrichPluginFactory()
        # Load Plugins
