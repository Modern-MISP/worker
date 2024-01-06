from kit.worker.email_worker.utility_email import getEmailSubjektMarkForEvent, getAnnounceBaseurl
from kit.worker.worker import Worker


class ContactEmailWorker(Worker):

    def run(self, event_id: int, message: str, creator_only: bool):

        #getEvent(event_id)

        if(creator_only):
            #getUser(Event[creatorId)
            pass
        else:
            #Datenbankabfrage getAllUsersInOrg(Event[orgId)
            pass

        getEmailSubjektMarkForEvent()

        getAnnounceBaseurl()


        pass
