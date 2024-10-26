import requests

from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.email.job_data import PostsEmailData
from mmisp.worker.jobs.email.posts_email_job import posts_email_job


def test_posts_email_job(init_api_config, post, user, site_admin_user):
    data: PostsEmailData = PostsEmailData(
        post_id=post.id, receiver_ids=[user.id], message="test message", title="test title"
    )
    posts_email_job(UserData(user_id=site_admin_user.id), data)

    response = requests.get("http://localhost:9000/api/messages")

    print("emailbonobo", response.json())
    assert response.status_code == 200
