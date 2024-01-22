from src.mmisp.worker.api.job_router.input_data import UserData
from src.mmisp.worker.job.email_job.job_data import ContactEmailData
from src.mmisp.worker.job.email_job.utility.email_config_data import EmailConfigData
from src.mmisp.worker.job.email_job.utility.smtp_client import SMTPClient
from src.mmisp.worker.job.job import Job


"""
Provides functionality for ContactEmailJob.
"""


class ContactEmailJob(Job):
    """
        Prepares the contact email and sends it.
    """

    __smtp_client: SMTPClient

    __config: EmailConfigData


    def run(self, requester: UserData, data: ContactEmailData):

        #getEvent8id)

        #requester = getUser(user_id)

        # for receiver_ids: recivers = getUSer(id)

        #getEmailSubjektMarkForEvent()

        #getAnnounceBaseurl()

        #smtp.getInstance

        #smtp.sendEmail
        pass

    def __init__(self):
        super().__init__()
        self.__config = EmailConfigData()
        self.__smtp_client = SMTPClient.get_instance(self.__config.__misp_email_address,
                                                     self.__config.__email_password,
                                                     self.__config.__misp_port,
                                                     self.__config.__smtp_host)