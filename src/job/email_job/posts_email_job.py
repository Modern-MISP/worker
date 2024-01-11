from pydantic import BaseModel

from src.api.job_router.input_data import UserData
from src.job.job import Job


class PostsEmailData(BaseModel):
    event_id: int
    post_id: int
    title: str
    message: str


"""
Provides functionality for PostsEmailJob.
"""


class PostsEmailJob(Job):

    """
    Prepares the posts email and sends it.
    """
    def run(self, user_data: UserData, data: PostsEmailData):

        #getPost(post_id) datenbankabfrage

        if(event_id == 0):
            #getThread(post[post][thread_id]
            #getUser(thread.user_id) nimmt nur den thredowner
            pass
        else:
            #getEvent(event_id)
            #Datenbankabfrage getAllUsersInOrg(Event[orgId)
            pass

        #Datenbankabfrage getUsersDieImThreadGeschriebenHaben()
        pass
