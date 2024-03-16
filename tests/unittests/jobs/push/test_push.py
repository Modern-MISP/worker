from unittest import TestCase

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.jobs.sync.push.job_data import PushResult, PushData
from tests.mocks.sync.push.test_push_job import test_push_job


class TestPush(TestCase):

    def test_push_full(self):
        user_data: UserData = UserData(user_id=1)
        push_data: PushData = PushData(server_id=1, technique="full")

        result: PushResult = test_push_job(user_data, push_data)
        self.assertEqual(1, 1)

    def test_push_incremental(self):
        user_data: UserData = UserData(user_id=1)
        push_data: PushData = PushData(server_id=1, technique="incremental")

        result: PushResult = test_push_job(user_data, push_data)
        self.assertEqual(1, 1)
