import requests

from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.email.contact_email_job import contact_email_job
from mmisp.worker.jobs.email.job_data import ContactEmailData
from mmisp.worker.jobs.email.utility.email_config_data import EmailConfigData


def test_contact_email_job(init_api_config, event, instance_owner_org_admin_user, site_admin_user):
    config: EmailConfigData = EmailConfigData()
    response = requests.get(f"http://{config.mmisp_smtp_host}:9000/api/messages")

    requester: UserData = UserData(user_id=site_admin_user.id)
    data: ContactEmailData = ContactEmailData(event_id=event.id, message="test message",
                                              receiver_ids=[instance_owner_org_admin_user.id])
    contact_email_job(requester, data)

    response = requests.get(f"http://{config.mmisp_smtp_host}:9000/api/messages")
    assert response.status_code == 200
