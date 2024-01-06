from kit.worker.email_worker.utility_email import getAnnounceBaseurl
from kit.worker.worker import Worker


class AlertEmailWorker(Worker):

    def run(self, event_id: int, old_publish: str):

        #getUser(user_id)

        #find(event_id)

        #notificationLogcheck()

        # Datenbankabfrage getAllUsersInOrg(Event[orgId)

        #fetchEmail() TODO

        getAnnounceBaseurl()



        pass
