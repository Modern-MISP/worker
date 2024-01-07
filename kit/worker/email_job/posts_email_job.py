from kit.worker.job import Job


class PostsEmailJob(Job):

    def run(self, event_id: int, post_id: int, title: str, message: str):

        #getPost(post_id) datenbankabfrage TODO Dataklasse

        if(event_id == 0):
            #getThread(post[post][thread_id] TODO Dataklasse
            #getUsers(thread.user_id)
            pass
        else:
            #getEvent(event_id)
            #Datenbankabfrage getAllUsersInOrg(Event[orgId)
            pass

        #Datenbankabfrage getUsersDieImThreadGeschriebenHaben()
        pass
