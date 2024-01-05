from kit.worker.worker import Worker


class PostsEmailWorker(Worker):

    def run(self, event_id: int, post_id: int, title: str, message: str):

        #getPost(post_id) datenbankabfrage TODO

        if(event_id == 0):
            #getThread(post[post][thread_id] TODO
            #getUsers(thread.user_id)
            pass
        else:
            #getEvent(event_id)
            #Datenbankabfrage getAllUsersInOrg(Event[orgId)
            pass
        pass
