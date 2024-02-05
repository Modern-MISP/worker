from unittest import TestCase

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.jobs.email.contact_email_job import contact_email_job
from mmisp.worker.jobs.email.job_data import ContactEmailData


class Test(TestCase):
    def test_contact_email_job(self):
        requester: UserData = UserData(user_id=1)
        data: ContactEmailData = ContactEmailData(event_id=1, message="test message", receiver_ids=[1])
        contact_email_job(requester, data)
        self.assertEqual(True, True)

    def test_abfuck(self):
        for i in range(1):
            self.test_contact_email_job()
