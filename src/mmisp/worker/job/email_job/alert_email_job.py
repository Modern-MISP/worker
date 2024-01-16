from mmisp.worker.job.email_job.job_data import AlertEmailData
from mmisp.worker.job.email_job.utility.email_config_data import EmailConfigData
from mmisp.worker.job.email_job.utility.smtp_client import SMTPClient
from mmisp.worker.job.job import Job


"""
Provides functionality for AlertEmailJob.
"""


class AlertEmailJob(Job):
    """
        Prepares the alert email and sends it.
    """

    __config: EmailConfigData

    __smtp_client: SMTPClient


    def run(self, data: AlertEmailData):

        #getEvent(event_id)

        # get_announce_baseurl()

        #getEmailSUbjektMark

        #for receivers do: getUsers

        #smt.getInstance

        #smtpSendEmail


        pass

    def __init__(self):
        super().__init__()
        self.__config = EmailConfigData()
        self.__smtp_client = SMTPClient.get_instance(self.__config.__misp_email_address,
                                                     self.__config.__email_password,
                                                     self.__config.__misp_port,
                                                     self.__config.__smtp_host)

