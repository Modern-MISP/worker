from pydantic import BaseModel

from src.api.job_router.input_data import UserData
from src.job.email_job.job_data import ContactEmailData
from src.job.job import Job


"""
Provides functionality for ContactEmailJob.
"""


class ContactEmailJob(Job):
    """
        Prepares the contact email and sends it.
    """
    def run(self, requester: UserData, data: ContactEmailData):

        #getEvent8id)

        #requester = getUser(user_id)

        # for receiver_ids: recivers = getUSer(id)

        #getEmailSubjektMarkForEvent()

        #getAnnounceBaseurl()

        #smtp.getInstance

        #smtp.sendEmail
        pass
