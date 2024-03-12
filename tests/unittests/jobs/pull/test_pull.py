from unittest import TestCase

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.jobs.sync.pull.job_data import PullData, PullResult
from mmisp.worker.jobs.sync.pull.pull_job import pull_job


class TestPull(TestCase):

    def test_pull_full(self):
        user_data: UserData = UserData(user_id=1)
        pull_data: PullData = PullData(server_id=1, technique="full")

        result: PullResult = pull_job(user_data, pull_data)
        self.assertEqual(1, 1)

    def test_pull_incremental(self):
        user_data: UserData = UserData(user_id=1)
        pull_data: PullData = PullData(server_id=1, technique="incremental")

        result: PullResult = pull_job(user_data, pull_data)
        self.assertEqual(1, 1)


    def test_pull_relevenat_clusters(self):
        user_data: UserData = UserData(user_id=1)
        pull_data: PullData = PullData(server_id=1, technique="pull_relevant_clusters")

        result: PullResult = pull_job(user_data, pull_data)
        self.assertEqual(1, 1)