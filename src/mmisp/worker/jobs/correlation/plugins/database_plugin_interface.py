from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute


class DatabasePluginInterface:
    """
    Encapsulates the relevant functions for the plugins to access the database.
    Only queries are supported, not methods to modify the database.
    """
    def __init__(self, misp_sql: MispSQL):
        self.__misp_sql = misp_sql

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

    def get_attributes_with_correlations(self, value: str) -> list[MispEventAttribute]:
        return self.__misp_sql.get_attributes_with_correlations(value)

    def get_number_of_correlations(self, value: str, only_correlation_table: bool) -> int:
        return self.__misp_sql.get_number_of_correlations(value, only_correlation_table)

    def get_threshold_for_over_correlating_values(self) -> int:
        """return CorrelationWorker.get_threshold()
        circular import!!!
        """
        pass
