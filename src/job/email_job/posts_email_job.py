from pydantic import BaseModel

from src.job.job import Job


class PostsEmailData(BaseModel):
    eventId: int
    postId: int
    title: str
    message: str


"""
Provides functionality for PostsEmailJob.
"""


class PostsEmailJob(Job):

    """
    Prepares the posts email and sends it.
    """
    def run(self, data: PostsEmailData):

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
