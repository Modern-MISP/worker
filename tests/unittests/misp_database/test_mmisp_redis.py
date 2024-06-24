import unittest
from unittest.mock import patch, Mock

from redis import Redis

from mmisp.worker.misp_database.mmisp_redis import MMispRedis


class TestMMispRedis(unittest.TestCase):
    def test_get_enqueued_celery_tasks(self):
        with patch("mmisp.worker.misp_database.mmisp_redis.redis.Redis", autospec=True) as mock_redis:
            mock_redis_connection: Mock = Mock(spec=Redis)
            mock_redis.return_value = mock_redis_connection

            queue_name: str = "test_queue"
            queue_length: int = 5
            mock_redis_connection.llen.return_value = queue_length
            returned_queue_length: int = MMispRedis().get_enqueued_celery_tasks(queue_name)
            mock_redis_connection.llen.assert_called_with(queue_name)
            self.assertEqual(queue_length, returned_queue_length)
