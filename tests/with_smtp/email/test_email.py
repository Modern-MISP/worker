import pytest
import requests

from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.email.alert_email_job import alert_email_job
from mmisp.worker.jobs.email.contact_email_job import contact_email_job
from mmisp.worker.jobs.email.job_data import AlertEmailData, ContactEmailData
from mmisp.worker.jobs.email.queue import queue
from mmisp.worker.jobs.email.utility.email_config_data import EmailConfigData


@pytest.mark.asyncio
async def test_alert_email_job(init_api_config, event_sharing_group, instance_owner_org_admin_user, site_admin_user):
    event = event_sharing_group
    config: EmailConfigData = EmailConfigData()
    response = requests.get(f"http://{config.mmisp_smtp_host}:9000/api/messages")

    data: AlertEmailData = AlertEmailData(
        event_id=event.id, receiver_ids=[instance_owner_org_admin_user.id], old_publish=1722088063
    )
    async with queue:
        await alert_email_job.run(UserData(user_id=site_admin_user.id), data)

    response = requests.get(f"http://{config.mmisp_smtp_host}:9000/api/messages")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_contact_email_job(init_api_config, event, instance_owner_org_admin_user, site_admin_user):
    config: EmailConfigData = EmailConfigData()
    response = requests.get(f"http://{config.mmisp_smtp_host}:9000/api/messages")

    requester: UserData = UserData(user_id=site_admin_user.id)
    data: ContactEmailData = ContactEmailData(
        event_id=event.id, message="test message", receiver_ids=[instance_owner_org_admin_user.id]
    )
    async with queue:
        await contact_email_job.run(requester, data)

    response = requests.get(f"http://{config.mmisp_smtp_host}:9000/api/messages")
    assert response.status_code == 200
