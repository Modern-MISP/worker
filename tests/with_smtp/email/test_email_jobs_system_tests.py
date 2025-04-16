import pytest

from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.email.alert_email_job import alert_email_job
from mmisp.worker.jobs.email.job_data import AlertEmailData, ContactEmailData, PostsEmailData
from mmisp.worker.jobs.email.posts_email_job import posts_email_job
from mmisp.worker.jobs.email.queue import queue


@pytest.mark.asyncio
async def test_alert_email_job(init_api_config, instance_owner_org_admin_user, event_sharing_group, site_admin_user):
    event = event_sharing_group

    user = UserData(user_id=site_admin_user.id)
    data = AlertEmailData(event_id=event.id, old_publish="1706736785", receiver_ids=[instance_owner_org_admin_user.id])

    async with queue:
        result = await alert_email_job.run(user, data)
    print(result)
    assert True


@pytest.mark.asyncio
async def test_contact_email(init_api_config, instance_owner_org_admin_user, event, site_admin_user):
    user = UserData(user_id=site_admin_user.id)
    data = ContactEmailData(event_id=event.id, message="test message", receiver_ids=[instance_owner_org_admin_user.id])

    async with queue:
        result = await alert_email_job.run(user, data)
    print(result)


@pytest.mark.asyncio
async def test_posts_email(init_api_config, instance_owner_org_admin_user, post, site_admin_user):
    data = PostsEmailData(
        post_id=post.id, title="test", message="test message", receiver_ids=[instance_owner_org_admin_user.id]
    )
    user = UserData(user_id=site_admin_user.id)

    async with queue:
        result = await posts_email_job.run(user, data)

    print(result)
