from pydantic import BaseModel

from src.api.job_router.input_data import UserData
from src.job.job import Job


class ContactEmailData(BaseModel):
    event_id: int
    message: str
    receiver_ids: list[int]


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
