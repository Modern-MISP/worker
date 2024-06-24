import unittest
from typing import Self

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.jobs.correlation.correlation_worker import CorrelationWorker
from mmisp.worker.jobs.correlation.job_data import ChangeThresholdData


class TestCorrelationWorker(unittest.TestCase):
    def test_correlation_worker(self: Self):
        worker: CorrelationWorker = CorrelationWorker()
        data: ChangeThresholdData = ChangeThresholdData(new_threshold=25)
        user: UserData = UserData(user_id=66)
        worker.set_threshold(user, data)
        self.assertEqual(25, worker.threshold)

        data = ChangeThresholdData(new_threshold=0)
        worker.set_threshold(user, data)
        self.assertEqual(25, worker.threshold)
