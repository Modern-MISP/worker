from src.mmisp.worker.job.email_job.job_data import PostsEmailData
from src.mmisp.worker.job.email_job.utility.email_config_data import EmailConfigData
from src.mmisp.worker.job.email_job.utility.smtp_client import SMTPClient
from src.mmisp.worker.job.job import Job


"""
Provides functionality for PostsEmailJob.
"""


class PostsEmailJob(Job):

    """
    Prepares the posts email and sends it.
    """

    __smtp_client: SMTPClient

    __config: EmailConfigData

    def run(self, data: PostsEmailData):

        """
         env = EmailEnvironment.get_instance()
        template = env.get_template("test.html")
        template.render(Gemüse="Tomate")

        """

        #getPost(post_id) datenbankabfrage
        #getThread(post[post][thread_id]


        #getUser(user_id) vielleicht auch in sendEmail

        #smtp_client.send_mail




        pass

    def __init__(self):
        super().__init__()
        self.__config = EmailConfigData()
        self.__smtp_client = SMTPClient.get_instance(self.__config.__misp_email_address,
                                                     self.__config.__email_password,
                                                     self.__config.__misp_port,
                                                     self.__config.__smtp_host)