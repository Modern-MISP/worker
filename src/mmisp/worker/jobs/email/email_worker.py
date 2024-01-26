from mmisp.worker.jobs.email.utility.email_config_data import EmailConfigData
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from jinja2 import Environment, select_autoescape, FileSystemLoader


class EmailWorker:

    def __init__(self):
        self.__misp_api: MispAPI = MispAPI()
        self.__misp_sql: MispSQL = MispSQL()
        self.__config: EmailConfigData = EmailConfigData(misp_url="test", email_subject_tlp_string="strs",
                                                       misp_email_address='str', email_password="str",
                                                       smtp_port=1, smtp_host="str")
        self.__environment: Environment = Environment(loader=FileSystemLoader("templates"),
                                                    autoescape=select_autoescape())

    @property
    def misp_api(self) -> MispAPI:
        return self.__misp_api

    @property
    def misp_sql(self) -> MispSQL:
        return self.__misp_sql

    @property
    def config(self) -> EmailConfigData:
        return self.__config

    @property
    def environment(self) -> Environment:
        return self.__environment


email_worker: EmailWorker = EmailWorker()
