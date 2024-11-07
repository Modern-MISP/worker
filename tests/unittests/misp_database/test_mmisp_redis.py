from unittest.mock import Mock, patch

import pytest
from redis import Redis

from mmisp.worker.misp_database.mmisp_redis import MMispRedis


@pytest.mark.asyncio
async def test_get_enqueued_celery_tasks():
    with patch("mmisp.worker.misp_database.mmisp_redis.redis.Redis", autospec=True) as mock_redis:
        mock_redis_connection: Mock = Mock(spec=Redis)
        mock_redis.return_value = mock_redis_connection

        queue_name: str = "test_queue"
        queue_length: int = 5
        mock_redis_connection.llen.return_value = queue_length
        returned_queue_length: int = await MMispRedis().get_enqueued_celery_tasks(queue_name)
        mock_redis_connection.llen.assert_called_with(queue_name)

        assert queue_length == returned_queue_length
