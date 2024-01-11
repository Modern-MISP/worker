from pydantic import BaseModel

from src.job.job import Job


class AlertEmailData(BaseModel):
    receiver_ids: list[int]
    event_id: int
    old_publish: str
    unsubscribe_code: str


"""
Provides functionality for AlertEmailJob.
"""


class AlertEmailJob(Job):
    """
        Prepares the alert email and sends it.
    """
    def run(self, data: AlertEmailData):

        #getEvent(event_id)

        # get_announce_baseurl()

        #getEmailSUbjektMark

        #getUsers

        #smt.getInstance

        #smtpSendEmail


        pass
