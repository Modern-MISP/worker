import time
from time import sleep
from typing import Self
from unittest import TestCase
from uuid import UUID

from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.server import Server
from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.jobs.sync.push.job_data import PushData
from mmisp.worker.jobs.sync.push.push_job import push_job
from mmisp.worker.jobs.sync.push.push_worker import push_worker
from tests.unittests.jobs.sync.test_sync_helper import get_new_event


class TestPush(TestCase):
    def test_push_add_event_full(self: Self):
        new_event: AddEditGetEventDetails = get_new_event()
        self.assertTrue(push_worker.misp_api.save_event(new_event))

        user_data: UserData = UserData(user_id=52)
        push_data: PushData = PushData(server_id=1, technique="full")

        push_job(user_data, push_data)

        server: Server = push_worker.misp_api.get_server(1)

        # if event wasn't pushed to remote-server it throws Exception
        push_worker.misp_api.get_event(UUID(new_event.uuid), server)
        self.assertEqual(1, 1)

    def test_push_add_event_incremental(self: Self):
        new_event: AddEditGetEventDetails = get_new_event()
        self.assertTrue(push_worker.misp_api.save_event(new_event))

        user_data: UserData = UserData(user_id=52)
        push_data: PushData = PushData(server_id=1, technique="incremental")

        push_job(user_data, push_data)

        server: Server = push_worker.misp_api.get_server(1)

        # if event wasn't pushed to remote-server it throws Exception
        push_worker.misp_api.get_event(UUID(new_event.uuid), server)
        self.assertEqual(1, 1)

    def test_push_edit_event_full(self: Self):
        # create new event
        new_event: AddEditGetEventDetails = get_new_event()
        self.assertTrue(push_worker.misp_api.save_event(new_event))

        user_data: UserData = UserData(user_id=52)
        push_data: PushData = PushData(server_id=1, technique="full")

        push_job(user_data, push_data)

        server: Server = push_worker.misp_api.get_server(1)

        # if event wasn't pushed to remote-server it throws Exception
        push_worker.misp_api.get_event(UUID(new_event.uuid), server)

        sleep(5)
        # edit event
        new_event.info = "edited" + new_event.info
        new_event.timestamp = str(int(time.time()))
        new_event.publish_timestamp = str(int(time.time()))
        self.assertTrue(push_worker.misp_api.update_event(new_event, server))

        push_job(user_data, push_data)

        # tests if event was updated on remote-server
        remote_event: AddEditGetEventDetails = push_worker.misp_api.get_event(UUID(new_event.uuid))
        self.assertEqual(remote_event.info, new_event.info)

    def test_push_edit_event_incremental(self: Self):
        # create new event
        new_event: AddEditGetEventDetails = get_new_event()
        self.assertTrue(push_worker.misp_api.save_event(new_event))

        user_data: UserData = UserData(user_id=52)
        push_data: PushData = PushData(server_id=1, technique="incremental")

        push_job(user_data, push_data)

        server: Server = push_worker.misp_api.get_server(1)

        # if event wasn't pushed to remote-server it throws Exception
        push_worker.misp_api.get_event(UUID(new_event.uuid), server)

        sleep(5)
        # edit event
        new_event.info = "edited" + new_event.info
        new_event.timestamp = str(int(time.time()))
        new_event.publish_timestamp = str(int(time.time()))
        self.assertTrue(push_worker.misp_api.update_event(new_event, server))

        push_job(user_data, push_data)

        # tests if event was updated on remote-server
        remote_event: AddEditGetEventDetails = push_worker.misp_api.get_event(UUID(new_event.uuid))
        self.assertEqual(remote_event.info, new_event.info)
