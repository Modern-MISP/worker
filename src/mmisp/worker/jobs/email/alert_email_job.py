import email
from email.message import EmailMessage
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from streaq import WrappedContext

from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.sharing_groups import ShortSharingGroup
from mmisp.db.database import sessionmanager
from mmisp.lib.logger import add_ajob_db_log, get_jobs_logger
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.email.job_data import AlertEmailData
from mmisp.worker.jobs.email.utility.email_config_data import EmailConfigData
from mmisp.worker.jobs.email.utility.utility_email import UtilityEmail
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import get_threat_level

from .queue import queue

db_logger = get_jobs_logger(__name__)
p = Path(__file__).parent / "templates"


@queue.task()
@add_ajob_db_log
async def alert_email_job(ctx: WrappedContext[None], user: UserData, data: AlertEmailData) -> None:
    """
    prepares an alert email by filling and rendering a template. afterward it will be sent to all specified users.
    :param user: the user who requested the job
    :type user: UserData
    :param data: contains data for the template and the user ids who will receive the emails.
    :type data: AlertEmailData
    """
    assert sessionmanager is not None

    __TEMPLATE_NAME: str = "alert_email.j2"
    __SUBJECT: str = (
        "[MISP] event: {event_id} - event info: {event_info} - thread level: {thread_level_name} - {tag_name}"
    )
    config: EmailConfigData = EmailConfigData()
    environment: Environment = Environment(loader=FileSystemLoader(Path(p)), autoescape=select_autoescape())

    email_msg: EmailMessage = email.message.EmailMessage()

    async with sessionmanager.session() as session:
        misp_api = MispAPI(session)
        event: AddEditGetEventDetails = await misp_api.get_event(data.event_id)
        thread_level: str = await get_threat_level(session, event.threat_level_id)

        if event.sharing_group_id is not None:
            event_sharing_group: ShortSharingGroup | None = (
                await misp_api.get_sharing_group(event.sharing_group_id)
            ).SharingGroup
        else:
            event_sharing_group = None

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

        await UtilityEmail.send_emails(
            misp_api,
            config.mmisp_email_address,
            config.mmisp_email_username,
            config.mmisp_email_password,
            config.mmisp_smtp_port,
            config.mmisp_smtp_host,
            data.receiver_ids,
            email_msg,
        )
