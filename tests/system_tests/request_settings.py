import json

from mmisp.worker.misp_database.misp_api_config import misp_api_config_data

old_misp_url: str = misp_api_config_data.url
old_misp_headers: json = {
    "Authorization": misp_api_config_data.key,
    "Content-Type": "application/json",
    "Accept": "application/json",
}
