import requests
from requests import Response

from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin import EnrichmentPluginInfo
from system_tests import request_settings


def is_plugin_available(plugin_name: str) -> bool:
    get_plugins_url: str = f"{request_settings.url}/worker/enrichment/plugins"
    get_plugins_response: Response = requests.get(get_plugins_url, headers=request_settings.headers)
    assert get_plugins_response.status_code == 200, \
        f"Enrichment Plugins could not be fetched. {get_plugins_response.json()}"

    for plugin in get_plugins_response.json():
        if EnrichmentPluginInfo.model_validate(plugin).NAME == plugin_name:
            return True

    return False
