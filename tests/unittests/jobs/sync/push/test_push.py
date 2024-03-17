import time
from datetime import datetime
from time import sleep
from unittest import TestCase

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.jobs.sync.pull.job_data import PullData, PullResult
from mmisp.worker.jobs.sync.pull.pull_job import pull_job
from mmisp.worker.jobs.sync.push.job_data import PushResult, PushData
from mmisp.worker.jobs.sync.push.push_job import push_job
from mmisp.worker.jobs.sync.push.push_worker import push_worker
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_server import MispServer
# from tests.mocks.sync.push.push_job import push_job
# from tests.mocks.sync.push.push_worker import push_worker
from tests.unittests.jobs.sync.test_sync_helper import get_new_event


class TestPush(TestCase):

    def test_push_add_event_full(self):
        new_event: dict = get_new_event()
        self.assertTrue(push_worker.misp_api.save_event_dic(new_event))

        user_data: UserData = UserData(user_id=52)
        push_data: PushData = PushData(server_id=1, technique="full")

        push_job(user_data, push_data)

        server: MispServer = push_worker.misp_api.get_server(1)

        # if event wasn't pushed to remote-server it throws Exception
        push_worker.misp_api.get_event_by_uuid(new_event["uuid"], server)
        self.assertEqual(1, 1)

    def test_push_add_event_incremental(self):
        new_event: dict = get_new_event()
        self.assertTrue(push_worker.misp_api.save_event_dic(new_event))

        user_data: UserData = UserData(user_id=52)
        push_data: PushData = PushData(server_id=1, technique="incremental")

        push_job(user_data, push_data)

        server: MispServer = push_worker.misp_api.get_server(1)

        # if event wasn't pushed to remote-server it throws Exception
        push_worker.misp_api.get_event_by_uuid(new_event["uuid"], server)
        self.assertEqual(1, 1)

    def test_push_edit_event_full(self):
        # create new event
        new_event: dict = get_new_event()
        self.assertTrue(push_worker.misp_api.save_event_dic(new_event))

        user_data: UserData = UserData(user_id=52)
        push_data: PushData = PushData(server_id=1, technique="full")

        push_job(user_data, push_data)

        server: MispServer = push_worker.misp_api.get_server(1)

        # if event wasn't pushed to remote-server it throws Exception
        push_worker.misp_api.get_event_by_uuid(new_event["uuid"], server)

        sleep(5)
        # edit event
        new_event["info"] = "edited" + new_event["info"]
        new_event["timestamp"] = str(int(time.time()))
        new_event["publish_timestamp"] = str(int(time.time()))
        self.assertTrue(push_worker.misp_api.update_event_dic(new_event))

        push_job(user_data, push_data)

        # tests if event was updated on remote-server
        remote_event: MispEvent = push_worker.misp_api.get_event_by_uuid(new_event["uuid"], server)
        self.assertEqual(remote_event.info, new_event["info"])

    def test_push_edit_event_incremental(self):
        # create new event
        new_event: dict = get_new_event()
        self.assertTrue(push_worker.misp_api.save_event_dic(new_event))

        user_data: UserData = UserData(user_id=52)
        push_data: PushData = PushData(server_id=1, technique="incremental")

        push_job(user_data, push_data)

        server: MispServer = push_worker.misp_api.get_server(1)

        # if event wasn't pushed to remote-server it throws Exception
        push_worker.misp_api.get_event_by_uuid(new_event["uuid"], server)

        sleep(5)
        # edit event
        new_event["info"] = "edited" + new_event["info"]
        new_event["timestamp"] = str(int(time.time()))
        new_event["publish_timestamp"] = str(int(time.time()))
        self.assertTrue(push_worker.misp_api.update_event_dic(new_event))

        push_job(user_data, push_data)

        # tests if event was updated on remote-server
        remote_event: MispEvent = push_worker.misp_api.get_event_by_uuid(new_event["uuid"], server)
        self.assertEqual(remote_event.info, new_event["info"])
