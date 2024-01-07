
class MMispRedis:
    def get_last_pull_id(self) -> int:
        pass

    def set_last_pull_id(self, last_pull_id: int) -> None:
        pass

    def get_last_push_id(self) -> int:
        pass

    def set_last_push_id(self, last_push_id: int) -> None:
        pass

    def get_last_pull_id_for_event(self, event_id: int) -> int:
        pass

    def set_last_pull_id_for_event(self, event_id: int, last_pull_id: int) -> None:
        pass

    def get_last_push_id_for_event(self, event_id: int) -> int:
        pass

    def set_last_push_id_for_event(self, event_id: int, last_push_id: int) -> None:
        pass

    def getAmountOfAlertEntrys(org_id: str) -> int:
        pass
