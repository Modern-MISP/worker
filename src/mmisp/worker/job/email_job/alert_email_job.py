from jinja2 import Template

from mmisp.worker.job.email_job.job_data import AlertEmailData
from mmisp.worker.job.email_job.utility.email_config_data import EmailConfigData
from mmisp.worker.job.email_job.utility.email_environment import EmailEnvironment
from mmisp.worker.job.email_job.utility.smtp_client import SMTPClient
from mmisp.worker.job.email_job.utility.utility_email import UtilityEmail
from mmisp.worker.job.job import Job
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_user import MispUser

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

        event: MispEvent = MispAPI.get_event(data.event_id)
        # getEvent(event_id)

        url: str #TODO
        # get_announce_baseurl()

        tempo: str #todo
        UtilityEmail.get_email_subject_mark_for_event(event, tempo)
        # getEmailSUbjektMark

        receivers: list[MispUser] = []
        for user_id in data.receiver_ids:
            receivers.append(MispAPI.get_user(user_id))
        # for receivers do: getUsers

        email_environment: EmailEnvironment = EmailEnvironment.get_instance()

        template: Template = email_environment.get_template("alert_email_template.html")

        #TODo
        template_str: str = template.render(data="abc")

        self.__smtp_client.send_mail(template_str, receivers)
        # smt.getInstance

        # smtpSendEmail

        pass

    def __init__(self):
        super().__init__()
        self.__config = EmailConfigData(misp_url ="test", email_subject_tlp_string ="strs", misp_email_address ='str', email_password ="str",smtp_port = 1,smtp_host ="str")
        self.__smtp_client = SMTPClient.get_instance(self.__config.misp_email_address,
                                                     self.__config.email_password,
                                                     self.__config.smtp_port,
                                                     self.__config.smtp_host)
