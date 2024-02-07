from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_database.mmisp_redis import MMispRedis


class ProcessfreetextWorker:
    def __init__(self):
        self.__misp_api: MispAPI = MispAPI()
        self.__misp_sql: MispSQL = MispSQL()
        self.__mmisp_redis: MMispRedis = MMispRedis()

    @property
    def misp_sql(self) -> MispSQL:
        """
        the misp sql instance to use for database operations in the processfreetext jobs

        :return: returns the misp sql instance
        :rtype: MispSQL
        """
        return self.__misp_sql

    @property
    def mmisp_redis(self) -> MMispRedis:
        """
        the mmisp redis instance to use for caching in the processfreetext jobs

        :return: returns the mmisp redis instance
        :rtype: MMispRedis
        """
        return self.__mmisp_redis

    @property
    def misp_api(self) -> MispAPI:
        """
        the misp api instance to use for api operations in the processfreetext jobs

        :return: returns the misp api instance
        :rtype: MispAPI
        """
        return self.__misp_api


processfreetext_worker: ProcessfreetextWorker = ProcessfreetextWorker()
