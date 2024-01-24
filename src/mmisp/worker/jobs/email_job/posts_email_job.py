from mmisp.worker.job.email_job.job_data import PostsEmailData
from mmisp.worker.job.email_job.utility.email_config_data import EmailConfigData
from mmisp.worker.job.email_job.utility.smtp_client import SMTPClient
from mmisp.worker.job.job import Job


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
        self.__config = EmailConfigData(misp_url ="test", email_subject_tlp_string ="strs", misp_email_address ='str', email_password ="str",smtp_port = 1,smtp_host ="str")
        self.__smtp_client = SMTPClient.get_instance(self.__config.misp_email_address,
                                                     self.__config.email_password,
                                                     self.__config.smtp_port,
                                                     self.__config.smtp_host)