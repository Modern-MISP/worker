from pydantic import BaseModel

from src.api.job_router.input_data import UserData
from src.job.email_job.job_data import PostsEmailData
from src.job.job import Job


"""
Provides functionality for PostsEmailJob.
"""


class PostsEmailJob(Job):

    """
    Prepares the posts email and sends it.
    """
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
