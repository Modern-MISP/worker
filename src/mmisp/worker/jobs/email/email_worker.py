from mmisp.worker.jobs.email.utility.email_config_data import EmailConfigData
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from jinja2 import Environment, select_autoescape, FileSystemLoader

from pathlib import Path

p = Path(__file__).parent / "templates"


class EmailWorker:
    def __init__(self):
        self.__misp_api: MispAPI = MispAPI()
        self.__misp_sql: MispSQL = MispSQL()
        self.__config: EmailConfigData = EmailConfigData()
        self.__environment: Environment = Environment(loader=FileSystemLoader(Path(p)), autoescape=select_autoescape())

    @property
    def misp_api(self) -> MispAPI:
        """
        The MISP API object used to communicate with the MISP Backend.
        :return: the MispAPI object
        :rtype: MispAPI
        """
        return self.__misp_api

    @property
    def misp_sql(self) -> MispSQL:
        """
        The MISP SQL object used to communicate with the MISP Backend.
        :return: the MispSQL object
        :rtype: MispSQL
        """
        return self.__misp_sql

    @property
    def config(self) -> EmailConfigData:
        """
        Returns the config object used to load constants.
        :return: the config object
        :rtype: EmailConfigData
        """
        return self.__config

    @property
    def environment(self) -> Environment:
        """
        Returns the environment object to get templates.
        :return: the environment object
        :rtype: Environment
        """
        return self.__environment


email_worker: EmailWorker = EmailWorker()
