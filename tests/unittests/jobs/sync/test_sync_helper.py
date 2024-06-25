import time
import uuid
from datetime import datetime

from mmisp.api_schemas.events import AddEditGetEventDetails


def get_new_event() -> AddEditGetEventDetails:
    timestamp: str = str(int(time.time()))
    date: str = datetime.now().strftime("%Y-%m-%d")

    event_dict: dict = {
        "id": "9",
        "orgc_id": "1",
        "org_id": "1",
        "date": date,
        "threat_level_id": "1",
        "info": f"Unit-Test Connected Communities {timestamp}",
        "published": True,
        "uuid": str(uuid.uuid4()),
        "attribute_count": "1",
        "analysis": "0",
        "timestamp": "1710602463",
        "distribution": "2",
        "proposal_email_lock": False,
        "locked": False,
        "publish_timestamp": "1710602471",
        "sharing_group_id": "0",
        "disable_correlation": False,
        "extends_uuid": "",
        "protected": None,
        "event_creator_email": "admin@admin.test",
        "Org": {"id": "1", "name": "ORGNAME", "uuid": "3f327efb-c12b-4d90-8b7d-7c9c06ef4941", "local": True},
        "Orgc": {"id": "1", "name": "ORGNAME", "uuid": "3f327efb-c12b-4d90-8b7d-7c9c06ef4941", "local": True},
        "Attribute": [
            {
                "id": "8",
                "type": "comment",
                "category": "Other",
                "to_ids": False,
                "uuid": str(uuid.uuid4()),
                "event_id": "9",
                "distribution": "5",
                "timestamp": "1710602311",
                "comment": "asdf",
                "sharing_group_id": "0",
                "deleted": False,
                "disable_correlation": False,
                "object_id": "0",
                "object_relation": None,
                "first_seen": None,
                "last_seen": None,
                "value": "asdf",
                "Galaxy": [],
                "ShadowAttribute": [],
            }
        ],
        "ShadowAttribute": [],
        "RelatedEvent": [],
        "Galaxy": [],
        "Object": [],
        "EventReport": [],
        "CryptographicKey": [],
    }

    return AddEditGetEventDetails.parse_obj(event_dict)
