import unittest

from mmisp.worker.jobs.correlation.correlation_worker import CorrelationWorker
from mmisp.worker.jobs.correlation.job_data import ChangeThresholdData


class TestCorrelationWorker(unittest.TestCase):
    def test_correlation_worker(self):
        worker: CorrelationWorker = CorrelationWorker()
        data: ChangeThresholdData = ChangeThresholdData(new_threshold=25)
        worker.set_threshold(data)
        self.assertEqual(25, worker.threshold)
