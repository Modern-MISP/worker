import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.server import Server
from mmisp.worker.jobs.sync.sync_config_data import SyncConfigData
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import filter_blocked_events
from mmisp.worker.misp_dataclasses.misp_minimal_event import MispMinimalEvent

log = logging.getLogger(__name__)


async def _get_mini_events_from_server(
    session: AsyncSession,
    ignore_filter_rules: bool,
    local_event_ids: list[int],
    config: SyncConfigData,
    misp_api: MispAPI,
    remote_server: Server,
) -> list[MispMinimalEvent]:
    use_event_blocklist: bool = config.misp_enable_event_blocklisting
    use_org_blocklist: bool = config.misp_enable_org_blocklisting
    local_event_ids_dic: dict[UUID, AddEditGetEventDetails] = await _get_local_events_dic(local_event_ids, misp_api)

    remote_event_views: list[MispMinimalEvent] = await misp_api.get_minimal_events(ignore_filter_rules, remote_server)
    remote_event_views = await filter_blocked_events(
        session, remote_event_views, use_event_blocklist, use_org_blocklist
    )
    remote_event_views = _filter_old_events(local_event_ids_dic, remote_event_views)

    return remote_event_views


def _filter_old_events(
    local_event_ids_dic: dict[UUID, AddEditGetEventDetails], events: list[MispMinimalEvent]
) -> list[MispMinimalEvent]:
    out: list[MispMinimalEvent] = []
    for event in events:
        uuid: UUID = UUID(event.uuid)
        if uuid not in local_event_ids_dic:
            out.append(event)
        else:
            # smallest possible date for none
            local_timestamp = local_event_ids_dic[uuid].timestamp or datetime(1, 1, 1)
            if event.timestamp > local_timestamp and local_event_ids_dic[uuid].locked:
                out.append(event)
    return out


async def _get_local_events_dic(local_event_ids: list[int], misp_api: MispAPI) -> dict[UUID, AddEditGetEventDetails]:
    out: dict[UUID, AddEditGetEventDetails] = {}
    for event_id in local_event_ids:
        try:
            event: AddEditGetEventDetails = await misp_api.get_event(event_id)
        except Exception as e:
            log.warning(f"Error while getting event {event_id} from local MISP: {e}")
            continue
        out[UUID(event.uuid)] = event
    return out
