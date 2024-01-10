from pydantic import BaseModel


from src.job.job import Job


class ContactEmailData(BaseModel):
    eventId: int
    message: str
    creatorOnly: bool


"""
Provides functionality for ContactEmailJob.
"""


class ContactEmailJob(Job):
    """
        Prepares the contact email and sends it.
    """
    def run(self, data: ContactEmailData):

        #getUser(user_id)

        #getEvent(event_id) bzw fetchEvent ka, ob ich des noch ändern muss

        if(creator_only):
            #getUser(Event[creatorId)
            pass
        else:
            #Datenbankabfrage getAllUsersInOrg(Event[orgId)
            pass

        #getEmailSubjektMarkForEvent()

        #getAnnounceBaseurl()
        pass
