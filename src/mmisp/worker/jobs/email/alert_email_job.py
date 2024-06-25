import email
from email.message import EmailMessage

from jinja2 import Environment

from mmisp.api_schemas.sharing_groups import SharingGroup
from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.jobs.email.email_worker import email_worker
from mmisp.worker.jobs.email.job_data import AlertEmailData
from mmisp.worker.jobs.email.utility.email_config_data import EmailConfigData
from mmisp.worker.jobs.email.utility.utility_email import UtilityEmail
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.api_schemas.events import AddEditGetEventDetails


@celery_app.task
def alert_email_job(user: UserData, data: AlertEmailData):
    """
    prepares an alert email by filling and rendering a template. afterward it will be sent to all specified users.
    :param user: the user who requested the job
    :type user: UserData
    :param data: contains data for the template and the user ids who will receive the emails.
    :type data: alertemaildata
    """

    __TEMPLATE_NAME: str = "alert_email.j2"
    __SUBJECT: str = (
        "[MISP] event: {event_id} - event info: {event_info} - thread level: {thread_level_name} - {tag_name}"
    )

    environment: Environment = email_worker.environment
    config: EmailConfigData = email_worker.config

    misp_sql: MispSQL = email_worker.misp_sql
    misp_api: MispAPI = email_worker.misp_api

    email_msg: EmailMessage = email.message.EmailMessage()

    event: AddEditGetEventDetails = misp_api.get_event(data.event_id)
    thread_level: str = misp_sql.get_threat_level(event.threat_level_id)

    if event.sharing_group_id is not None:
        event_sharing_group: SharingGroup = misp_api.get_sharing_group(event.sharing_group_id).SharingGroup
    else:
        event_sharing_group: dict = {"name": "None"}

    email_msg["From"] = config.mmisp_email_address
    email_msg["Subject"] = __SUBJECT.format(
        event_id=data.event_id,
        event_info=event.info,
        thread_level_name=thread_level,
        tag_name=UtilityEmail.get_email_subject_mark_for_event(event, config.email_subject_string),
    )

    template = environment.get_template(__TEMPLATE_NAME)
    email_msg.set_content(
        template.render(
            mmisp_url=config.mmisp_url,
            event=event,
            event_sharing_group=event_sharing_group,
            event_thread_level=thread_level,
            old_publish_timestamp=data.old_publish,
        )
    )

    UtilityEmail.send_emails(
        config.mmisp_email_address,
        config.mmisp_email_password,
        config.mmisp_smtp_port,
        config.mmisp_smtp_host,
        data.receiver_ids,
        email_msg,
    )
