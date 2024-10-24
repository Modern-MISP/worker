import os

from mmisp.worker.config import ENV_PREFIX
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import enrichment_plugin_factory
from mmisp.worker.plugins.loader import PluginLoader


def main() -> None:
    # load enrichment plugins
    enrichment_plugin_env = f"{ENV_PREFIX}_ENRICHMENT_PLUGIN_DIRECTORY"
    enrichment_plugin_dir = os.environ.get(enrichment_plugin_env, None)
    if enrichment_plugin_dir is not None:
        PluginLoader.load_plugins_from_directory(enrichment_plugin_dir, enrichment_plugin_factory)

    worker = celery_app.Worker()
    worker.start()


if __name__ == "__main__":
    main()
