from streaq import Worker

from mmisp.worker.redis_config import redis_config

queue: Worker = Worker(redis_url=redis_config.redis_url(), queue_name="correlation")
