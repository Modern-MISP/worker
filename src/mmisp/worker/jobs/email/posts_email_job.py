import email
from email.message import EmailMessage
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from streaq import WrappedContext

from mmisp.db.database import sessionmanager
from mmisp.db.models.post import Post
from mmisp.lib.logger import add_ajob_db_log, get_jobs_logger
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.email.job_data import PostsEmailData
from mmisp.worker.jobs.email.utility.email_config_data import EmailConfigData
from mmisp.worker.jobs.email.utility.utility_email import UtilityEmail
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import get_post

# from mmisp.worker.misp_database.misp_api import MispAPI
from .queue import queue

db_logger = get_jobs_logger(__name__)
p = Path(__file__).parent / "templates"


@queue.task()
@add_ajob_db_log
async def posts_email_job(ctx: WrappedContext[None], user: UserData, data: PostsEmailData) -> None:
    """
    Prepares a posts email by filling and rendering a template. Afterward it will be sent to all specified users.
    :param user: the user who requested the job
    :type user: UserData
    :param data: contains data for the template and the user ids who will receive the emails.
    :type data: PostsEmailData
    """
    assert sessionmanager is not None
    __SUBJECT: str = "New post in discussion: {thread_id} - {tlp}"
    __TEMPLATE_NAME: str = "posts_email.j2"

    # environment: Environment = email_worker.environment
    # config: EmailConfigData = email_worker.config
    #    self.__misp_api: MispAPI = MispAPI()
    config: EmailConfigData = EmailConfigData()
    environment: Environment = Environment(loader=FileSystemLoader(Path(p)), autoescape=select_autoescape())

    email_msg: EmailMessage = email.message.EmailMessage()

    async with sessionmanager.session() as session:
        misp_api = MispAPI(session)
        post: Post = await get_post(session, data.post_id)

        email_msg["From"] = config.mmisp_email_address
        email_msg["Subject"] = __SUBJECT.format(thread_id=post.thread_id, tlp=config.email_subject_string)
        template = environment.get_template(__TEMPLATE_NAME)
        email_msg.set_content(
            template.render(
                title=data.title,
                mmisp_url=config.mmisp_url,
                thread_id=post.thread_id,
                post_id=data.post_id,
                message=data.message,
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
