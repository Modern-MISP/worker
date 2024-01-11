from pydantic import BaseModel

from src.api.job_router.input_data import UserData
from src.job.job import Job


class PostsEmailData(BaseModel):
    post_id: int
    title: str
    message: str
    receiver_ids: list[int]


"""
Provides functionality for PostsEmailJob.
"""


class PostsEmailJob(Job):

    """
    Prepares the posts email and sends it.
    """
    def run(self, user_data: UserData, data: PostsEmailData):

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
