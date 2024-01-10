import redis


class MMispRedis:
    def __init__(self):
        self.__redis_connection = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def get_last_pull_id_for_event(self, event_id: int) -> int:
        pass

    def get_last_push_id_for_event(self, event_id: int) -> int:
        pass

    """
    getlist und zähle mit forschleife, wieviele einträge
    """
    def get_amount_of_alert_entries(self, org_id: int) -> int:
        pass

    """
    fügt neuen timestamp hinzu, und set die ttl neu auf 24 stunden
    """
    def set_new_org_alert_entry(self, org_id: int) -> None:
        pass

    """
    löscht alle alten timestamps aus liste
    """
    def delete_old_org_alert_entries(self, org_id) -> None:
        pass

    def set_last_pull_id_for_event(self, event_id: int, last_pull_id: int) -> None:
        pass

    def set_last_push_id_for_event(self, event_id: int, last_push_id: int) -> None:
        pass
