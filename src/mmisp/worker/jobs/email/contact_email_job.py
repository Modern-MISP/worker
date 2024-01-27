from email.message import EmailMessage
import email

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.jobs.email.email_worker import email_worker
from mmisp.worker.jobs.email.job_data import ContactEmailData
from mmisp.worker.jobs.email.utility.email_config_data import EmailConfigData
from mmisp.worker.jobs.email.utility.smtp_client import SmtpClient
from mmisp.worker.jobs.email.utility.utility_email import UtilityEmail
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_dataclasses.misp_user import MispUser
from jinja2 import Environment


"""
Provides functionality for ContactEmailJob.
"""


@celery_app.task
def contact_email_job(requester: UserData, data: ContactEmailData):
    """
    Prepares the contact email and sends it.
    """

    # getEvent8id)

    # requester = getUser(user_id)

    # for receiver_ids: recivers = getUSer(id)

    # getEmailSubjektMarkForEvent()

    # getAnnounceBaseurl()

    # smtp.getInstance

    # smtp.sendEmail

    __TEMPLATE_NAME: str = "contact_email.html"
    __SUBJECT: str = "Need info about event {event_id} - {tlp}"

    environment: Environment = email_worker.environment
    config: EmailConfigData = email_worker.config
    misp_sql: MispSQL = email_worker.misp_sql
    misp_api: MispAPI = email_worker.misp_api

    email_msg: EmailMessage = email.message.EmailMessage()
    smtp_client: SmtpClient = SmtpClient(config.smtp_host, config.smtp_port)

    requester_misp: MispUser = misp_api.get_user(requester.user_id)

    email_msg['From'] = config.email_from
    email_msg['Subject'] = __SUBJECT.format(event_id=data.event_id, tlp=UtilityEmail.get_email_subject_mark_for_event())
    template = environment.get_template(__TEMPLATE_NAME)
    email_msg.set_content(template.render(requester_email=requester_misp.email, message=data.message,
                                          misp_url=config.misp_url, event_id=data.event_id))

    smtp_client.openSmtpConnection(config.misp_email_address, config.misp_email_password)

    for receiver_id in data.receivers:
        user: MispUser = misp_api.get_user(receiver_id)
        email_msg['To'] = user.email
        smtp_client.sendEmail(config.email_from, user.email, email_msg.as_string())

    smtp_client.closeSmtpConnection()
    pass
