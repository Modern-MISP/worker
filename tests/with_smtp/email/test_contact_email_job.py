from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.email.contact_email_job import contact_email_job
from mmisp.worker.jobs.email.job_data import ContactEmailData


def test_contact_email_job():
    requester: UserData = UserData(user_id=1)
    data: ContactEmailData = ContactEmailData(event_id=2, message="test message", receiver_ids=[1])
    contact_email_job(requester, data)
