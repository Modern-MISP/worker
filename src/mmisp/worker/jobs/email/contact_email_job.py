import email
from email.message import EmailMessage
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from streaq import WrappedContext

from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.db.database import sessionmanager
from mmisp.lib.logger import add_ajob_db_log, get_jobs_logger
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.email.job_data import ContactEmailData
from mmisp.worker.jobs.email.utility.email_config_data import EmailConfigData
from mmisp.worker.jobs.email.utility.utility_email import UtilityEmail
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_dataclasses.misp_user import MispUser

from .queue import queue

db_logger = get_jobs_logger(__name__)
p = Path(__file__).parent / "templates"


@queue.task()
@add_ajob_db_log
async def contact_email_job(ctx: WrappedContext[None], requester: UserData, data: ContactEmailData) -> None:
    """
    Prepares a contact email by filling and rendering a template. Afterward it will be sent to all specified users.
    :param requester: is the user who wants to contact the users
    :type requester: UserData
    :param data: contains data for the template and the user ids who will receive the emails.
    :type data: ContactEmailData
    """
    assert sessionmanager is not None
    __TEMPLATE_NAME: str = "contact_email.j2"
    __SUBJECT: str = "Need info about event {event_id} - {tag_name}"

    config: EmailConfigData = EmailConfigData()
    environment: Environment = Environment(loader=FileSystemLoader(Path(p)), autoescape=select_autoescape())

    email_msg: EmailMessage = email.message.EmailMessage()

    async with sessionmanager.session() as session:
        misp_api = MispAPI(session)
        requester_misp: MispUser = await misp_api.get_user(requester.user_id)
        event: AddEditGetEventDetails = await misp_api.get_event(data.event_id)

        email_msg["From"] = config.mmisp_email_address
        email_msg["Subject"] = __SUBJECT.format(
            event_id=data.event_id,
            tag_name=UtilityEmail.get_email_subject_mark_for_event(event, config.email_subject_string),
        )

        template = environment.get_template(__TEMPLATE_NAME)
        email_msg.set_content(
            template.render(
                requestor_email=requester_misp.email,
                message=data.message,
                mmisp_url=config.mmisp_url,
                event_id=data.event_id,
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
