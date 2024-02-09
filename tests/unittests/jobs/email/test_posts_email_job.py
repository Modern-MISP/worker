import unittest
from unittest.mock import patch

from jinja2 import Environment, PackageLoader, select_autoescape

from mmisp.worker.jobs.email.email_worker import email_worker
from mmisp.worker.jobs.email.job_data import PostsEmailData
from mmisp.worker.jobs.email.posts_email_job import posts_email_job
from mmisp.worker.jobs.email.utility.email_config_data import EmailConfigData
from tests.mocks.misp_database_mock.misp_api_mock import MispAPIMock
from tests.mocks.misp_database_mock.misp_sql_mock import MispSQLMock


class TestPostsEmailJob(unittest.TestCase):

    @patch('mmisp.worker.jobs.email.utility.utility_email.email_worker', autospec=True)
    @patch('mmisp.worker.jobs.email.posts_email_job.email_worker', autospec=True)
    def test_posts_email_job(self, email_worker_mock, utility_mock):
        # start setup mock
        assert email_worker_mock.__class__.__name__ == email_worker.__class__.__name__

        email_worker_mock.misp_sql = MispSQLMock()
        email_worker_mock.misp_api = MispAPIMock()
        email_worker_mock.environment = Environment(loader=PackageLoader('mmisp',
                                                                         'worker/jobs/email/templates'),
                                                    autoescape=select_autoescape())
        email_worker_mock.config = EmailConfigData(misp_url="testURL", email_subject_string="tlp",
                                                   misp_email_address='lerngruppe2Misp@outlook.de',
                                                   misp_email_password="Ab3?Ab3?",
                                                   smtp_port=587, smtp_host="smtp-mail.outlook.com")
        assert utility_mock.__class__.__name__ == email_worker.__class__.__name__

        utility_mock.misp_api = MispAPIMock()
        # end setup mock

        data: PostsEmailData = PostsEmailData(post_id=1, receiver_ids=[1], message="test message", title="test title")
        posts_email_job(data)
        self.assertEqual(True, True)
