from kit.worker.enrichment_worker.plugins.enrichment_plugin_factory import EnrichmentPluginFactory


class EnrichWorker:

    def __init__(self):
        self.plugin_factory = EnrichmentPluginFactory()
        # Load Plugins
