from mmisp.worker.jobs.email.utility.email_config_data import EmailConfigData
from mmisp.worker.jobs.email.utility.smtp_client import SMTPClient
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from jinja2 import Environment, PackageLoader, select_autoescape


class EmailWorker:

    def __init__(self):
        self.misp_api: MispAPI = MispAPI()
        self.misp_sql: MispSQL = MispSQL()
        self.config: EmailConfigData = EmailConfigData(misp_url="test", email_subject_tlp_string="strs",
                                                       misp_email_address='str', email_password="str",
                                                       smtp_port=1, smtp_host="str")
        self.smtp_client: SMTPClient = SMTPClient(self.config.misp_email_address, self.config.email_password,
                                                  self.config.smtp_port, self.config.smtp_host)
        self.environment: Environment = Environment(loader=PackageLoader("src"), autoescape=select_autoescape())


email_worker: EmailWorker = EmailWorker()
