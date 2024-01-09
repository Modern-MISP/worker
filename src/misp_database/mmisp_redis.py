import redis


class MMispRedis:
    def __init__(self):
        self.__redis_connection = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def get_last_pull_id(self) -> int:
        pass

    def get_last_push_id(self) -> int:
        pass

    def get_last_pull_id_for_event(self, event_id: int) -> int:
        pass

    def get_last_push_id_for_event(self, event_id: int) -> int:
        pass

    def get_amount_of_alert_entries(self, org_id: int) -> int:
        pass

    def set_last_pull_id(self, last_pull_id: int) -> None:
        pass

    def set_last_push_id(self, last_push_id: int) -> None:
        pass

    def set_last_pull_id_for_event(self, event_id: int, last_pull_id: int) -> None:
        pass

    def set_last_push_id_for_event(self, event_id: int, last_push_id: int) -> None:
        pass
