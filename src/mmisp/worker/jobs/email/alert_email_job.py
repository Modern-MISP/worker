import email
from email.message import EmailMessage

from jinja2 import Template, Environment

from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.jobs.email.email_worker import email_worker
from mmisp.worker.jobs.email.job_data import AlertEmailData
from mmisp.worker.jobs.email.utility.email_config_data import EmailConfigData
from mmisp.worker.jobs.email.utility.smtp_client import SmtpClient
from mmisp.worker.jobs.email.utility.utility_email import UtilityEmail
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_sharing_group import MispSharingGroup
from mmisp.worker.misp_dataclasses.misp_thread import MispThread
from mmisp.worker.misp_dataclasses.misp_user import MispUser

"""
Provides functionality for AlertEmailJob.

Prepares the alert email and sends it.
"""


@celery_app.task
def alert_email_job(data: AlertEmailData):
    """
    Prepares the contact email and sends it.
    """

    __TEMPLATE_NAME: str = "alert_email.j2"
    __SUBJECT: str = "Event: {event_id} - {event_info} - {thread_level_name} - {tlp}"

    environment: Environment = email_worker.environment
    config: EmailConfigData = email_worker.config
    misp_sql: MispSQL = email_worker.misp_sql
    misp_api: MispAPI = email_worker.misp_api

    email_msg: EmailMessage = email.message.EmailMessage()
    smtp_client: SmtpClient = SmtpClient(config.smtp_host, config.smtp_port)

    event: MispEvent = misp_api.get_event(data.event_id)
    thread_level: MispThread = misp_sql.get_thread(event.thread_id)
    #event_orgc: TODO
    #event_org: MispOrg = misp_api.get TODO
    #event_sharing_group: MispSharingGroup todo

    email_msg['From'] = config.misp_email_address
    email_msg['Subject'] = __SUBJECT.format(event_id=data.event_id, event_info=event.info,
                                            thread_level_name=thread_level.name,
                                            tlp=UtilityEmail.get_email_subject_mark_for_event(
                                                event, config.misp_email_address))

    template = environment.get_template(__TEMPLATE_NAME)
    email_msg.set_content(template.render(misp_url=config.misp_url, event=event, event_orgc="todo", event_org="TODO",
                                          event_sharing_group="todo", event_thread_level=thread_level,
                                          old_publish_timestamp=data.old_publish))

    smtp_client.openSmtpConnection(config.misp_email_address, config.misp_email_password)

    for receiver_id in data.receivers:
        user: MispUser = misp_api.get_user(receiver_id)
        email_msg['To'] = user.email
        smtp_client.sendEmail(config.misp_email_address, user.email, email_msg.as_string())

    smtp_client.closeSmtpConnection()
