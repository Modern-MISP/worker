
class MispDatabaseRedis:
    def set_last_pull_id(self, event_id: int, id: int) -> None:
        pass

    def get_last_pull_id(self, event_id: int) -> int:
        pass

    def set_last_push_id(self, event_id: int, id: int) -> None:
        pass

    def get_last_push_id(self, event_id: int) -> int:
        pass

    def set_tc_entry(self) -> bool:
        """
        Set the top correlations entry in the redis database.
        """
        pass
