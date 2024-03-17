import email
from email.message import EmailMessage

from jinja2 import Environment

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.jobs.email.email_worker import email_worker
from mmisp.worker.jobs.email.job_data import ContactEmailData
from mmisp.worker.jobs.email.utility.email_config_data import EmailConfigData
from mmisp.worker.jobs.email.utility.utility_email import UtilityEmail
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_user import MispUser


@celery_app.task
def contact_email_job(requester: UserData, data: ContactEmailData):
    """
    Prepares a contact email by filling and rendering a template. Afterward it will be sent to all specified users.
    :param requester: is the user who wants to contact the users
    :type requester: UserData
    :param data: contains data for the template and the user ids who will receive the emails.
    :type data: ContactEmailData
    """

    __TEMPLATE_NAME: str = "contact_email.j2"
    __SUBJECT: str = "Need info about event {event_id} - {tag_name}"

    environment: Environment = email_worker.environment
    config: EmailConfigData = email_worker.config
    misp_api: MispAPI = email_worker.misp_api

    email_msg: EmailMessage = email.message.EmailMessage()

    requester_misp: MispUser = misp_api.get_user(requester.user_id)
    event: MispEvent = misp_api.get_event(data.event_id)

    email_msg['From'] = config.mmisp_email_address
    email_msg['Subject'] = __SUBJECT.format(event_id=data.event_id,
                                            tag_name=UtilityEmail.
                                            get_email_subject_mark_for_event(event, config.email_subject_string))

    template = environment.get_template(__TEMPLATE_NAME)
    email_msg.set_content(template.render(requestor_email=requester_misp.email, message=data.message,
                                          mmisp_url=config.mmisp_url, event_id=data.event_id))

    UtilityEmail.send_emails(config.mmisp_email_address, config.mmisp_email_password, config.mmisp_smtp_port,
                             config.mmisp_smtp_host, data.receiver_ids, email_msg)
