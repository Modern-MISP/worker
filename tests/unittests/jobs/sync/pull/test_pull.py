import time
from time import sleep
from unittest import TestCase

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.jobs.sync.pull.job_data import PullData
from mmisp.worker.jobs.sync.pull.pull_job import pull_job
from mmisp.worker.jobs.sync.pull.pull_worker import pull_worker
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_server import MispServer
from tests.unittests.jobs.sync.test_sync_helper import get_new_event


class TestPull(TestCase):

    def test_pull_add_event_full(self):
        server: MispServer = pull_worker.misp_api.get_server(1)
        new_event: dict = get_new_event()
        self.assertTrue(pull_worker.misp_api.save_event_dic(new_event, server))

        user_data: UserData = UserData(user_id=52)
        pull_data: PullData = PullData(server_id=1, technique="full")

        pull_job(user_data, pull_data)

        # if event wasn't pulled to local-server it throws Exception
        pull_worker.misp_api.get_event_by_uuid(new_event["uuid"])
        self.assertEqual(1, 1)

    def test_pull_add_event_incremental(self):
        server: MispServer = pull_worker.misp_api.get_server(1)
        new_event: dict = get_new_event()
        self.assertTrue(pull_worker.misp_api.save_event_dic(new_event, server))

        user_data: UserData = UserData(user_id=52)
        pull_data: PullData = PullData(server_id=1, technique="full")

        pull_job(user_data, pull_data)

        # if event wasn't pulled to local-server it throws Exception
        pull_worker.misp_api.get_event_by_uuid(new_event["uuid"])
        self.assertEqual(1, 1)

    def test_pull_edit_event_full(self):
        # create new event
        server: MispServer = pull_worker.misp_api.get_server(1)
        new_event: dict = get_new_event()
        self.assertTrue(pull_worker.misp_api.save_event_dic(new_event, server))

        user_data: UserData = UserData(user_id=52)
        pull_data: PullData = PullData(server_id=1, technique="full")

        pull_job(user_data, pull_data)


        # if event wasn't pulled to local-server it throws Exception
        pull_worker.misp_api.get_event_by_uuid(new_event["uuid"])

        sleep(5)
        # edit event
        new_event["info"] = "edited" + new_event["info"]
        new_event["timestamp"] = str(int(time.time()))
        new_event["publish_timestamp"] = str(int(time.time()))
        self.assertTrue(pull_worker.misp_api.update_event_dic(new_event, server))

        pull_job(user_data, pull_data)

        # tests if event was updated on local-server
        remote_event: MispEvent = pull_worker.misp_api.get_event_by_uuid(new_event["uuid"])
        self.assertEqual(remote_event.info, new_event["info"])

    def test_pull_edit_event_incremental(self):
        # create new event
        server: MispServer = pull_worker.misp_api.get_server(1)
        new_event: dict = get_new_event()
        self.assertTrue(pull_worker.misp_api.save_event_dic(new_event, server))

        user_data: UserData = UserData(user_id=52)
        pull_data: PullData = PullData(server_id=1, technique="full")

        pull_job(user_data, pull_data)


        # if event wasn't pulled to local-server it throws Exception
        pull_worker.misp_api.get_event_by_uuid(new_event["uuid"])

        sleep(5)
        # edit event
        new_event["info"] = "edited" + new_event["info"]
        new_event["timestamp"] = str(int(time.time()))
        new_event["publish_timestamp"] = str(int(time.time()))
        self.assertTrue(pull_worker.misp_api.update_event_dic(new_event, server))

        pull_job(user_data, pull_data)

        # tests if event was updated on local-server
        remote_event: MispEvent = pull_worker.misp_api.get_event_by_uuid(new_event["uuid"])
        self.assertEqual(remote_event.info, new_event["info"])
