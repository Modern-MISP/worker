from src.worker.email_job.utility_email import get_announce_baseurl
from src.worker.job import Job

"""
Provides functionality for AlertEmailJob.
"""
class AlertEmailJob(Job):
    """
        Prepares the alert email and sends it.
    """
    def run(self, event_id: int, old_publish: str):

        #getUser(user_id)

        #find(event_id)

        #notificationLogcheck()

        # Datenbankabfrage getAllUsersInOrg(Event[orgId)

        #fetchEmail()

        get_announce_baseurl()



        pass
