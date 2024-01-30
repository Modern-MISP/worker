from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_object import MispObject


class DatabasePluginInterface:
    """
    Encapsulates the relevant functions for the plugins to access the database.
    Only queries are supported, not methods to modify the database.
    """
    def __init__(self, misp_sql: MispSQL, misp_api: MispAPI, threshold: int):
        self.__misp_sql = misp_sql
        self.threshold = threshold
        self.__misp_api = misp_api

    def get_values_with_correlation(self) -> list[str]:
        return self.__misp_sql.get_values_with_correlation()

    def get_over_correlating_values(self) -> list[tuple[str, int]]:
        return self.__misp_sql.get_over_correlating_values()

    def get_excluded_correlations(self) -> list[str]:
        return self.__misp_sql.get_excluded_correlations()

    def is_excluded_correlation(self, value: str) -> bool:
        return self.__misp_sql.is_excluded_correlation(value)

    def is_over_correlating_value(self, value: str) -> bool:
        return self.__misp_sql.is_over_correlating_value(value)

    def get_attributes_with_same_value(self, value: str) -> list[MispEventAttribute]:
        return self.__misp_sql.get_attributes_with_same_value(value)

    def get_number_of_correlations(self, value: str, only_correlation_table: bool) -> int:
        return self.__misp_sql.get_number_of_correlations(value, only_correlation_table)

    def get_event(self, event_id: int) -> MispEvent:
        return self.__misp_api.get_event(event_id)

    def get_event_attribute(self, attribute_id: int) -> MispEventAttribute:
        return self.__misp_api.get_event_attribute(attribute_id)

    def get_event_attributes(self, event_id: int) -> list[MispEventAttribute]:
        return self.__misp_api.get_event_attributes(event_id)

    def get_object(self, object_id: int) -> MispObject:
        return self.__misp_api.get_object(object_id)

    @property
    def misp_sql(self):
        """
        Method to prevent the access to the misp_sql object.
        """
        return

    @property
    def misp_api(self):
        """
        Method to prevent the access to the misp_api object.
        """
        return
