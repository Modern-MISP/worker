from fastapi.testclient import TestClient
from requests import Response

from mmisp.plugins.enrichment.enrichment_plugin import EnrichmentPluginInfo

from ... import request_settings


def is_plugin_available(plugin_name: str, client: TestClient) -> bool:
    get_plugins_url: str = f"{request_settings.url}/worker/enrichment/plugins"
    get_plugins_response: Response = client.get(get_plugins_url, headers=request_settings.headers)
    assert (
        get_plugins_response.status_code == 200
    ), f"Enrichment Plugins could not be fetched. {get_plugins_response.json()}"

    for plugin in get_plugins_response.json():
        if EnrichmentPluginInfo.parse_obj(plugin).NAME == plugin_name:
            return True

    return False
