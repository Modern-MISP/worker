import redis

from mmisp.worker.misp_database.mmisp_redis_config import mmisp_redis_config_data, MMispRedisConfigData


class MMispRedis:
    """
    Encapsulates the connection to the MMISP Redis database.
    """

    def __init__(self, config: MMispRedisConfigData = mmisp_redis_config_data):
        self._config: MMispRedisConfigData = config
        self._redis_connection = redis.Redis(host=self._config.host,
                                             port=self._config.port,
                                             db=self._config.db,
                                             username=self._config.username,
                                             password=self._config.password,
                                             decode_responses=True)

    def get_enqueued_celery_tasks(self, queue: str) -> int:
        """
        Returns the number of enqueued celery tasks in the given queue.
        :param queue: The queue name.
        :type queue: str
        """

        return self._redis_connection.llen(queue)
