from kit.worker.email_job.utility_email import getEmailSubjektMarkForEvent, getAnnounceBaseurl
from kit.worker.job import Job


class ContactEmailJob(Job):

    def run(self, event_id: int, message: str, creator_only: bool):

        #getUser(user_id)

        #getEvent(event_id) bzw fetchEvent ka, ob ich des noch ändern muss

        if(creator_only):
            #getUser(Event[creatorId)
            pass
        else:
            #Datenbankabfrage getAllUsersInOrg(Event[orgId)
            pass

        getEmailSubjektMarkForEvent()

        getAnnounceBaseurl()


        pass
