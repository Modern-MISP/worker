from unittest.mock import patch

from jinja2 import Environment, PackageLoader, select_autoescape

from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.email.email_worker import email_worker
from mmisp.worker.jobs.email.job_data import PostsEmailData
from mmisp.worker.jobs.email.posts_email_job import posts_email_job
from mmisp.worker.jobs.email.utility.email_config_data import EmailConfigData
from tests.mocks.misp_database_mock.misp_api_mock import MispAPIMock
from tests.mocks.misp_database_mock.misp_sql_mock import MispSQLMock


@patch("mmisp.worker.jobs.email.utility.utility_email.email_worker", autospec=True)
@patch("mmisp.worker.jobs.email.posts_email_job.email_worker", autospec=True)
def test_posts_email_job(email_worker_mock, utility_mock, post):
    # start setup mock
    assert email_worker_mock.__class__.__name__ == email_worker.__class__.__name__

    email_worker_mock.misp_sql = MispSQLMock()
    email_worker_mock.misp_api = MispAPIMock()
    email_worker_mock.environment = Environment(
        loader=PackageLoader("mmisp", "worker/jobs/email/templates"), autoescape=select_autoescape()
    )
    email_worker_mock.config = EmailConfigData(
        mmisp_url="testURL",
        email_subject_string="tlp",
        mmisp_email_address=email_worker.config.mmisp_email_address,
        mmisp_email_password=email_worker.config.mmisp_email_password,
        mmisp_smtp_port=email_worker.config.mmisp_smtp_port,
        mmisp_smtp_host=email_worker.config.mmisp_smtp_host,
    )
    assert utility_mock.__class__.__name__ == email_worker.__class__.__name__

    utility_mock.misp_api = MispAPIMock()
    # end setup mock

    data: PostsEmailData = PostsEmailData(
        post_id=post.id, receiver_ids=[1, 2, 3], message="test message", title="test title"
    )
    posts_email_job(UserData(user_id=66), data)
