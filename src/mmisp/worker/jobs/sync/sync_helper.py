import logging
from uuid import UUID

from mmisp.worker.jobs.sync.sync_config_data import SyncConfigData
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_event_view import MispMinimalEvent
from mmisp.worker.misp_dataclasses.misp_server import MispServer

log = logging.getLogger(__name__)


def _get_mini_events_from_server(ignore_filter_rules: bool, local_event_ids: list[int], config: SyncConfigData,
                                 misp_api: MispAPI, misp_sql: MispSQL, remote_server: MispServer) \
        -> list[MispMinimalEvent]:
    use_event_blocklist: bool = config.misp_enable_event_blocklisting
    use_org_blocklist: bool = config.misp_enable_org_blocklisting
    local_event_ids_dic: dict[UUID, MispEvent] = _get_local_events_dic(local_event_ids, misp_api)

    remote_event_views: list[MispMinimalEvent] = misp_api.get_minimal_events(ignore_filter_rules,
                                                                             remote_server)
    remote_event_views = misp_sql.filter_blocked_events(remote_event_views, use_event_blocklist,
                                                        use_org_blocklist)
    remote_event_views = _filter_old_events(local_event_ids_dic, remote_event_views)
    # remote_event_views = _filter_empty_events(remote_event_views)

    return remote_event_views


def _filter_old_events(local_event_ids_dic: dict[UUID, MispEvent], events: list[MispMinimalEvent]) -> list[
    MispMinimalEvent]:
    out: list[MispMinimalEvent] = []
    for event in events:
        if event.uuid not in local_event_ids_dic or (
                not event.timestamp <= local_event_ids_dic[UUID(event.uuid)].timestamp
                and not local_event_ids_dic[UUID(event.uuid)].locked):
            out.append(event)
    return out


# def _filter_empty_events(events: list[MispEvent]) -> list[MispEvent]:
#     pass


def _get_local_events_dic(local_event_ids: list[int], misp_api: MispAPI) -> dict[UUID, MispEvent]:
    out: dict[UUID, MispEvent] = {}
    for event_id in local_event_ids:
        try:
            event: MispEvent = misp_api.get_event(event_id)
        except Exception as e:
            log.warning(f"Error while getting event {event_id} from local MISP: {e}")
            continue
        out[event.uuid] = event
    return out
