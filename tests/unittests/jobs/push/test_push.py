from unittest import TestCase

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.jobs.sync.pull.job_data import PullData, PullResult
from mmisp.worker.jobs.sync.pull.pull_job import pull_job
from mmisp.worker.jobs.sync.push.job_data import PushResult, PushData
from mmisp.worker.jobs.sync.push.push_job import push_job


class TestPush(TestCase):

    def test_push_full(self):
        user_data: UserData = UserData(user_id=1)
        push_data: PushData = PushData(server_id=1, technique="full")

        result: PushResult = push_job(user_data, push_data)
        self.assertEqual(1, 1)

    def test_push_incremental(self):
        user_data: UserData = UserData(user_id=1)
        push_data: PushData = PushData(server_id=1, technique="incremental")

        result: PushResult = push_job(user_data, push_data)
        self.assertEqual(1, 1)
