from email.message import EmailMessage
import email

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.jobs.email.email_worker import email_worker
from mmisp.worker.jobs.email.job_data import PostsEmailData
from mmisp.worker.jobs.email.utility.email_config_data import EmailConfigData
from mmisp.worker.jobs.email.utility.utility_email import UtilityEmail
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_dataclasses.misp_post import MispPost
from jinja2 import Environment


@celery_app.task
def posts_email_job(user: UserData, data: PostsEmailData):
    """
    Prepares a posts email by filling and rendering a template. Afterward it will be sent to all specified users.
    :param user: the user who requested the job
    :type user: UserData
    :param data: contains data for the template and the user ids who will receive the emails.
    :type data: PostsEmailData
    """
    __SUBJECT: str = "New post in discussion: {thread_id} - {tlp}"
    __TEMPLATE_NAME: str = "posts_email.j2"

    environment: Environment = email_worker.environment
    config: EmailConfigData = email_worker.config

    misp_sql: MispSQL = email_worker.misp_sql

    email_msg: EmailMessage = email.message.EmailMessage()

    post: MispPost = misp_sql.get_post(data.post_id)

    email_msg['From'] = config.mmisp_email_address
    email_msg['Subject'] = __SUBJECT.format(thread_id=post.thread_id, tlp=config.email_subject_string)
    template = environment.get_template(__TEMPLATE_NAME)
    email_msg.set_content(template.render(title=data.title, mmisp_url=config.mmisp_url, thread_id=post.thread_id,
                                          post_id=data.post_id, message=data.message, ))

    UtilityEmail.send_emails(config.mmisp_email_address, config.mmisp_email_password, config.mmisp_smtp_port,
                             config.mmisp_smtp_host, data.receiver_ids, email_msg)
