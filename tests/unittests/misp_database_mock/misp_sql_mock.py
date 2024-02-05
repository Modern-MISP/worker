import datetime
import unittest

from mmisp.worker.misp_dataclasses.misp_post import MispPost
from mmisp.worker.misp_dataclasses.misp_thread import MispThread


class MispSQLMock:

    def get_event_tag_id(self, event_id: int, tag_id: int) -> int:
        return 1

    def get_attribute_tag_id(self, attribute_id: int, tag_id: int) -> int:
        if attribute_id == 1 and tag_id == 2:
            return 10
        elif attribute_id == 1 and tag_id == 3:
            return 11
        return 1

    def get_post(self, post_id: int) -> MispPost:
        match post_id:
            case 1: return MispPost(id=1,
                                    date_created="2023 - 11 - 16",
                                    date_modified="2023 - 11 - 16",
                                    user_id=1,
                                    contents="test content",
                                    post_id=1,
                                    thread_id=1)

    def get_thread(self, thread_id: int) -> MispThread:
        match thread_id:
            case 1: return MispThread(id=1, date_created=datetime.datetime(2023, 11, 16, 0, 0),
                                      date_modified=datetime.datetime(2023, 11, 16, 0, 0),
                                      distribution=1, user_id=1, post_count=1, event_id=1, title="test title", org_id=1,
                                      sharing_group_id=1)

