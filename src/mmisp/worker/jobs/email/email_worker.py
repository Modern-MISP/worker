from pathlib import Path
from typing import Self

from jinja2 import Environment, FileSystemLoader, select_autoescape

from mmisp.worker.jobs.email.utility.email_config_data import EmailConfigData
from mmisp.worker.misp_database.misp_api import MispAPI

p = Path(__file__).parent / "templates"


class EmailWorker:
    def __init__(self: Self) -> None:
        self.__misp_api: MispAPI = MispAPI()
        self.__config: EmailConfigData = EmailConfigData()
        self.__environment: Environment = Environment(loader=FileSystemLoader(Path(p)), autoescape=select_autoescape())

    @property
    def misp_api(self: Self) -> MispAPI:
        """
        The MISP API object used to communicate with the MISP Backend.
        :return: the MispAPI object
        :rtype: MispAPI
        """
        return self.__misp_api

    @property
    def config(self: Self) -> EmailConfigData:
        """
        Returns the config object used to load constants.
        :return: the config object
        :rtype: EmailConfigData
        """
        return self.__config

    @property
    def environment(self: Self) -> Environment:
        """
        Returns the environment object to get templates.
        :return: the environment object
        :rtype: Environment
        """
        return self.__environment


email_worker: EmailWorker = EmailWorker()
