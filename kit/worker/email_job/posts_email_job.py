from kit.worker.job import Job

"""
Provides functionality for PostsEmailJob.
"""
class PostsEmailJob(Job):

    """
    Prepares the posts email and sends it.
    """
    def run(self, event_id: int, post_id: int, title: str, message: str):

        #getPost(post_id) datenbankabfrage

        if(event_id == 0):
            #getThread(post[post][thread_id]
            #getUsers(thread.user_id)
            pass
        else:
            #getEvent(event_id)
            #Datenbankabfrage getAllUsersInOrg(Event[orgId)
            pass

        #Datenbankabfrage getUsersDieImThreadGeschriebenHaben()
        pass
