from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.email.contact_email_job import contact_email_job
from mmisp.worker.jobs.email.job_data import ContactEmailData


def test_contact_email_job(init_api_config, event, instance_owner_org_admin_user, site_admin_user):
    requester: UserData = UserData(user_id=site_admin_user.id)
    data: ContactEmailData = ContactEmailData(event_id=event.id, message="test message",
                                              receiver_ids=[instance_owner_org_admin_user.id])
    contact_email_job(requester, data)
