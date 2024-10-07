import json

from mmisp.worker.config.system_config_data import system_config_data
from mmisp.worker.misp_database.misp_api_config import misp_api_config_data

headers: json = {"Authorization": f"Bearer {system_config_data.api_key}"}

old_misp_url: str = misp_api_config_data.url
old_misp_headers: json = {
    "Authorization": misp_api_config_data.key,
    "Content-Type": "application/json",
    "Accept": "application/json",
}
