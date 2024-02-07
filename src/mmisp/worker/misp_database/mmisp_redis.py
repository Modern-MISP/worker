import redis


class MMispRedis:
    def __init__(self):
        self.__redis_connection = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # def get_last_pull_id_for_event(self, event_id: int) -> int:
    #     pass
    #
    # def set_last_pull_id_for_event(self, event_id: int, last_pull_id: int) -> None:
    #     pass

    def get_enqueued_celery_tasks(self, queue: str) -> int:
        return self.__redis_connection.llen(queue)

    def get_last_push_id_for_event(self, event_id: int) -> int:
        """
        TODO used?

        :param event_id:
        :type event_id:
        :return:
        :rtype:
        """
        pass

    def set_last_push_id_for_event(self, event_id: int, last_push_id: int) -> None:
        """
        TODO used?

        :param event_id:
        :type event_id:
        :param last_push_id:
        :type last_push_id:
        :return:
        :rtype:
        """
        pass
