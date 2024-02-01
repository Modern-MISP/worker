from uuid import UUID

from mmisp.worker.jobs.sync.push.push_worker import push_worker
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_server import MispServer


def _get_event_views_from_server(ignore_filter_rules: bool, local_event_ids: list[int], remote_server: MispServer) \
        -> list[MispEvent]:
    use_event_blocklist: bool = push_worker.push_config.use_event_blocklist
    use_org_blocklist: bool = push_worker.push_config.use_org_blocklist
    local_event_ids_dic: dict[int, MispEvent] = _get_local_events_dic(local_event_ids)

    remote_event_views: list[MispEvent] = push_worker.misp_api.get_event_views_from_server(ignore_filter_rules,
                                                                                           remote_server)
    remote_event_views = push_worker.misp_sql.filter_blocked_events(remote_event_views, use_event_blocklist,
                                                                    use_org_blocklist)
    remote_event_views = _filter_old_events(local_event_ids_dic, remote_event_views)
    remote_event_views = _filter_empty_events(remote_event_views)

    return remote_event_views


def _filter_old_events(local_event_ids_dic, events) -> list[MispEvent]:
    out: list[MispEvent] = []
    for event in events:
        if (event.id in local_event_ids_dic and not event.timestamp <= local_event_ids_dic[event.id].timestamp
                and not local_event_ids_dic[event.id].locked):
            out.append(event)
    return out


def _filter_empty_events(events: list[MispEvent]) -> list[MispEvent]:
    pass


def _get_local_events_dic(local_event_uuids: list[UUID]) -> dict[UUID, MispEvent]:
    out: dict[UUID, MispEvent] = {}
    for event_id in local_event_uuids:
        event: MispEvent = push_worker.misp_api.get_event(event_id, None)
        out[event.uuid] = event
    return out
