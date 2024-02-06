import unittest

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.jobs.email.job_data import PostsEmailData
from mmisp.worker.jobs.email.posts_email_job import posts_email_job


class TestBasicAlertEmailJob(unittest.TestCase):

    def test_posts_email_job(self):
        data: PostsEmailData = PostsEmailData(event_id=1, receiver_ids=[1],
                                              old_publish=None)
        posts_email_job(data)
        self.assertEqual(True, True)
    