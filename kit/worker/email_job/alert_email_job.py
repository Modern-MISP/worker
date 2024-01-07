from kit.worker.email_job.utility_email import getAnnounceBaseurl
from kit.worker.job import Job


class AlertEmailJob(Job):

    def run(self, event_id: int, old_publish: str):

        #getUser(user_id)

        #find(event_id)

        #notificationLogcheck()

        # Datenbankabfrage getAllUsersInOrg(Event[orgId)

        #fetchEmail() TODO

        getAnnounceBaseurl()



        pass
