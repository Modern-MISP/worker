from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.jobs.email.job_data import PostsEmailData


"""
Provides functionality for PostsEmailJob.
"""


@celery_app.task
def posts_email_job(self, data: PostsEmailData):
    """
    Prepares the posts email and sends it.

    env = EmailEnvironment.get_instance()
    template = env.get_template("test.html")
    template.render(Gemüse="Tomate")
    """

    # getPost(post_id) datenbankabfrage
    # getThread(post[post][thread_id]
    # getUser(user_id) vielleicht auch in sendEmail
    # smtp_client.send_mail

    pass
