from pydantic import BaseModel

from src.job.job import Job


class AlertEmailData(BaseModel):
    event_id: int
    old_publish: str


"""
Provides functionality for AlertEmailJob.
"""


class AlertEmailJob(Job):
    """
        Prepares the alert email and sends it.
    """
    def run(self, data: AlertEmailData):

        #getEvent(event_id)

        #notificationLogcheck()

        # Datenbankabfrage getAllUsersInOrg(Event[orgId)

        #fetchEmail() nicht gemacht, brauch ich glaub ich nicht

        #get_announce_baseurl()
        pass
