from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.email.job_data import PostsEmailData
from mmisp.worker.jobs.email.posts_email_job import posts_email_job

# from mmisp.worker.jobs.email.utility.email_config_data import EmailConfigData


def test_posts_email_job(post):
    data: PostsEmailData = PostsEmailData(
        post_id=post.id, receiver_ids=[1, 2, 3], message="test message", title="test title"
    )
    posts_email_job(UserData(user_id=66), data)
