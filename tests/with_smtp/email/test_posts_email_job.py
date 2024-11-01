import requests

from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.email.job_data import PostsEmailData
from mmisp.worker.jobs.email.posts_email_job import posts_email_job
from mmisp.worker.jobs.email.utility.email_config_data import EmailConfigData


def test_posts_email_job(init_api_config, post, instance_owner_org_admin_user, site_admin_user):
    config: EmailConfigData = EmailConfigData()
    response = requests.get(f"http://{config.mmisp_smtp_host}:9000/api/messages")

    data: PostsEmailData = PostsEmailData(
        post_id=post.id, receiver_ids=[instance_owner_org_admin_user.id], message="test message", title="test title"
    )
    async_result = posts_email_job.delay(UserData(user_id=site_admin_user.id), data)
    async_result.get()

    response = requests.get(f"http://{config.mmisp_smtp_host}:9000/api/messages")

    assert response.status_code == 200
