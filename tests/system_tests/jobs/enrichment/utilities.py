from fastapi.testclient import TestClient
from requests import Response

from mmisp.plugins.enrichment.enrichment_plugin import EnrichmentPluginInfo


def is_plugin_available(plugin_name: str, client: TestClient, authorization_headers) -> bool:
    get_plugins_url: str = "/worker/enrichment/plugins"
    get_plugins_response: Response = client.get(get_plugins_url, headers=authorization_headers)
    assert get_plugins_response.status_code == 200, (
        f"Enrichment Plugins could not be fetched. {get_plugins_response.json()}"
    )

    for plugin in get_plugins_response.json():
        if EnrichmentPluginInfo.parse_obj(plugin).NAME == plugin_name:
            return True

    return False
