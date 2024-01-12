from pydantic import BaseModel

from src.job.email_job.job_data import AlertEmailData
from src.job.job import Job


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

        #for receivers do: getUsers

        #smt.getInstance

        #smtpSendEmail


        pass
