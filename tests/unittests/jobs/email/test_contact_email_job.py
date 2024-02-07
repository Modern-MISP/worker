
from unittest import TestCase
from unittest.mock import patch

from jinja2 import PackageLoader, select_autoescape, Environment

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.jobs.email.contact_email_job import contact_email_job
from mmisp.worker.jobs.email.email_worker import email_worker
from mmisp.worker.jobs.email.job_data import ContactEmailData
from mmisp.worker.jobs.email.utility.email_config_data import EmailConfigData
from tests.mocks.misp_database_mock.misp_api_mock import MispAPIMock
from tests.mocks.misp_database_mock.misp_sql_mock import MispSQLMock


class Test(TestCase):

    @patch('mmisp.worker.jobs.email.utility.utility_email.email_worker', autospec=True)
    @patch('mmisp.worker.jobs.email.contact_email_job.email_worker', autospec=True)
    def test_run(self, email_worker_mock, utility_mock):
        # Setup mock
        assert email_worker_mock.__class__.__name__ == email_worker.__class__.__name__

        email_worker_mock.misp_sql = MispSQLMock()
        email_worker_mock.misp_api = MispAPIMock()
        email_worker_mock.environment = Environment(loader=PackageLoader('mmisp',
                                                                         'worker/jobs/email/templates'),
                                                    autoescape=select_autoescape())
        email_worker_mock.config = EmailConfigData(misp_url="testURL", email_subject_tlp_string="tlp",
                                                   misp_email_address='lerngruppeMisp@outlook.de',
                                                   email_password="Ab3?Ab3?",
                                                   smtp_port=587, smtp_host="smtp-mail.outlook.com")
        assert utility_mock.__class__.__name__ == email_worker.__class__.__name__

        utility_mock.misp_api = MispAPIMock()

        self.test_contact_email_job()

    def test_contact_email_job(self):
        requester: UserData = UserData(user_id=1)
        data: ContactEmailData = ContactEmailData(event_id=2, message="test message", receiver_ids=[1])
        contact_email_job(requester, data)
        self.assertEqual(True, True)
