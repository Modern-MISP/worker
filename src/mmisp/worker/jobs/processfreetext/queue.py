from mmisp.worker.jobs.lazy_worker import LazyWorker
from mmisp.worker.redis_config import redis_config

queue: LazyWorker = LazyWorker(redis_url=redis_config.redis_url(), queue_name="processfreetext")
