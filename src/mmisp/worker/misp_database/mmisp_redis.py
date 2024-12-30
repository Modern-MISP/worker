from inspect import isawaitable
from typing import Self

import redis

from mmisp.worker.misp_database.mmisp_redis_config import MMispRedisConfigData, mmisp_redis_config_data


class MMispRedis:
    """
    Encapsulates the connection to the MMISP Redis database.
    """

    def __init__(self: Self, config: MMispRedisConfigData = mmisp_redis_config_data) -> None:
        self._config: MMispRedisConfigData = config
        self._redis_connection = redis.Redis(
            host=self._config.host,
            port=self._config.port,
            db=self._config.db,
            username=self._config.username,
            password=self._config.password,
            decode_responses=True,
        )

    async def get_enqueued_celery_tasks(self: Self, queue: str) -> int:
        """
        Returns the number of enqueued celery tasks in the given queue.

        Args:
            queue (str): The queue name.

        Returns:
            int: The number of enqueued celery tasks.
        """
        llen = self._redis_connection.llen(queue)
        if isawaitable(llen):
            return await llen
        else:
            assert isinstance(llen, int)
            return llen

    # TODO add type
    async def get_enqueued_celery_jobs(self: Self, queue_name: str):  # noqa
        """
        Returns the list of enqueued celery jobs in the given queue.

        Args:
            queue_name (str): The name of the queue.

        Returns:
            list: List of enqueued celery jobs.
        """
        items = self._redis_connection.lrange(queue_name, 0, -1)  # get all items from 0 to -1 (all items)
        if isawaitable(items):
            return await items
        else:
            assert isinstance(items, list)
            return items
