from email.message import EmailMessage
import email
from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.jobs.email.email_worker import email_worker
from mmisp.worker.jobs.email.job_data import PostsEmailData
from mmisp.worker.jobs.email.utility.email_config_data import EmailConfigData
from mmisp.worker.jobs.email.utility.smtp_client import SmtpClient
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_dataclasses.misp_post import MispPost
from mmisp.worker.misp_dataclasses.misp_user import MispUser
from jinja2 import Environment

"""
Provides functionality for PostsEmailJob.
"""


@celery_app.task
def posts_email_job(data: PostsEmailData):
    """
    Prepares the posts email and sends it.

    env = EmailEnvironment.get_instance()
    template = env.get_template("test.html")
    template.render(Gemüse="Tomate")
    """

    __SUBJECT: str = "New post in discussion: {thread_id} - {tlp}"
    __TEMPLATE_NAME: str = "posts_email.html"

    environment: Environment = email_worker.environment
    config: EmailConfigData = email_worker.config
    misp_sql: MispSQL = email_worker.misp_sql
    misp_api: MispAPI = email_worker.misp_api

    email_msg: EmailMessage = email.message.EmailMessage()
    smtp_client: SmtpClient = SmtpClient(config.smtp_host, config.smtp_port)

    post: MispPost = misp_sql.get_post(data.post_id)

    email_msg['From'] = config.email_from
    email_msg['Subject'] = __SUBJECT.format(thread_id=post.thread_id, tlp=config.email_subject_tlp_string)
    template = environment.get_template(__TEMPLATE_NAME)
    email_msg.set_content(template.render(title=data.title, misp_url=config.misp_url, thread_id=post.thread_id,
                                          post_id=data.post_id, message=data.message, ))

    smtp_client.openSmtpConnection(config.misp_email_address, config.misp_email_password)

    for receiver_id in data.receivers:
        user: MispUser = misp_api.get_user(receiver_id)
        email_msg['To'] = user.email
        smtp_client.sendEmail(config.email_from, user.email, email_msg.as_string())

    smtp_client.closeSmtpConnection()
    pass
