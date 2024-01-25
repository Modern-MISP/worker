from mmisp.worker.jobs.email.utility.email_config_data import EmailConfigData
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
        """self.environment: Environment = Environment(loader=FileSystemLoader("templates"), 
        autoescape=select_autoescape())"""


email_worker: EmailWorker = EmailWorker()
