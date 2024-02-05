from email.message import EmailMessage
import email

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery_app.celery_app import celery_app
from mmisp.worker.jobs.email.email_worker import email_worker
from mmisp.worker.jobs.email.job_data import ContactEmailData
from mmisp.worker.jobs.email.utility.email_config_data import EmailConfigData
from mmisp.worker.jobs.email.utility.utility_email import UtilityEmail
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_user import MispUser
from jinja2 import Environment, FileSystemLoader, select_autoescape

from tests.unittests.misp_database_mock.misp_api_mock import MispAPIMock


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
    __SUBJECT: str = "Need info about event {event_id} - {tlp}"

    environment: Environment = email_worker.environment
    config: EmailConfigData = email_worker.config
    misp_sql: MispSQL = email_worker.misp_sql
    misp_api: MispAPI = email_worker.misp_api

    bonobo_api: MispAPIMock = MispAPIMock()

    email_msg: EmailMessage = email.message.EmailMessage()

    requester_misp: MispUser = bonobo_api.get_user(requester.user_id)
    # requester_misp: MispUser = misp_api.get_user(requester.user_id)
    event: MispEvent = bonobo_api.get_event(data.event_id)
    # event: MispEvent = misp_api.get_event(data.event_id)

    email_msg['From'] = config.misp_email_address
    email_msg['Subject'] = __SUBJECT.format(event_id=data.event_id, tlp=UtilityEmail.get_email_subject_mark_for_event(
        event, config.email_subject_tlp_string))

    template = environment.get_template(__TEMPLATE_NAME)
    email_msg.set_content(template.render(requester_email=requester_misp.email, message=data.message,
                                          misp_url=config.misp_url, event_id=data.event_id))

    UtilityEmail.sendEmails(config.misp_email_address, config.email_password, config.smtp_port, config.smtp_host,
                            data.receiver_ids, email_msg)
