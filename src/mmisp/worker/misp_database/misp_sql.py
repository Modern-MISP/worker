from uuid import UUID

from mmisp.worker.misp_dataclasses.misp_correlation import MispCorrelation
from mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from mmisp.worker.misp_dataclasses.misp_post import MispPost
from mmisp.worker.misp_dataclasses.misp_proposal import MispProposal
from mmisp.worker.misp_dataclasses.misp_sharing_group import MispSharingGroup
from mmisp.worker.misp_dataclasses.misp_sighting import MispSighting
from mmisp.worker.misp_dataclasses.misp_tag import MispTag
from mmisp.worker.misp_dataclasses.misp_thread import MispThread

from sqlmodel import create_engine, or_


engine = create_engine('mysql://username:password@localhost/dbname') # TODO add real database

class MispSQL:

    @property
    @contextmanager
    def session(self):
        session = Session(autocommit=False, autoflush=False, bind=engine)
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_galaxy_clusters(self, options: str) -> list[MispGalaxyCluster]:
        pass

    def get_event_ids(self, param: str) -> list[int]:
        pass

    def get_tags(self, param: str) -> list[MispTag]:
        pass

    def get_sharing_groups(self) -> list[MispSharingGroup]:
        pass

    def filter_blocked_events(self, events: list[MispEvent], use_event_blocklist: bool, use_org_blocklist: bool) \
            -> list[MispEvent]:
        pass

    def filter_blocked_clusters(self, clusters: list[MispGalaxyCluster]) -> list[MispGalaxyCluster]:
        pass

    def get_attributes_with_same_value(self, value: str) -> list[MispEventAttribute]:
        session = self.session()
        statement = select(MispEventAttribute).where(or_(MispEventAttribute.value1 == value,
                                                         MispEventAttribute.value2 == value))
        result: list[MispEventAttribute] = session.exec(statement).all()
        return result

    def get_values_with_correlation(self) -> list[str]:
        session = self.session()
        correlation_values_table = Table('correlation_values', MetaData(), autoload_with=engine)
        statement = select(correlation_values_table.c.value)
        result: list[str] = session.exec(statement).all()
        return result

    def get_over_correlating_values(self) -> list[tuple[str, int]]:
        """
        Method to get all values from over_correlating_values table with their occurrence.
        :return: all values from over_correlating_values table with their occurrence
        :rtype: list[tuple[str, int]]
        """
        session = self.session()
        over_correlating_values_table = Table('over_correlating_values', MetaData(), autoload_with=engine)
        statement = select(over_correlating_values_table.c.value, over_correlating_values_table.c.occurrence)
        result: list[tuple[str, int]]  = session.exec(statement).all()
        return result

    def get_excluded_correlations(self) -> list[str]:
        """
        Method to get all values from correlation_exclusions table.
        :return: all values from correlation_exclusions table
        :rtype: list[str]
        """
        session = self.session()
        correlation_exclusions_table = Table('correlation_exclusions', MetaData(), autoload_with=engine)
        statement = select(correlation_exclusions_table.c.value)
        result = session.exec(statement).all()
        return result

    def get_thread(self, thread_id: str) -> MispThread:
        session = self.session()
        statement = select(MispThread).where(MispThread.id == thread_id)
        result: MispThread = session.exec(statement).first()
        return result

    def get_post(self, post_id: int) -> MispPost:
        session = self.session()
        statement = select(MispPost).where(MispPost.id == thread_id)
        result: MispThread = session.exec(statement).first()
        return result

    def is_excluded_correlation(self, value: str) -> bool:
        """
        Checks if value is in correlation_exclusions table.
        :param value: to check
        :type value: str
        :return: True if value is in correlation_exclusions table, False otherwise
        :rtype: bool
        """
        session = self.session()
        correlation_exclusions_table = Table('correlation_exclusions', MetaData(), autoload_with=engine)
        statement = select(correlation_exclusions_table).where(correlation_exclusions_table.c.value == value)
        result = session.exec(statement).all()
        if len(result) == 0:
            return False
        else:
            return True

    def is_over_correlating_value(self, value: str) -> bool:
        """
        Checks if value is in over_correlating_values table. Doesn't check if value has more correlations in the
        database than the current threshold.
        :param value: to check
        :type value: str
        :return: True if value is in over_correlating_values table, False otherwise
        :rtype: bool
        """
        session = self.session()
        over_correlating_values_table = Table('over_correlating_values', MetaData(), autoload_with=engine)
        statement = select(over_correlating_values_table).where(correlation_exclusions_table.c.value == value)
        result = session.exec(statement).all()
        if len(result) == 0:
            return False
        else:
            return True

    def save_proposal(self, proposal: MispProposal) -> bool:
        pass

    def save_sighting(self, sighting: MispSighting) -> bool:
        pass

    def get_number_of_correlations(self, value: str, only_correlation_table: bool) -> int:
        pass

    def add_correlation_value(self, value: str) -> int:
        # TODO value id erst holen wenn klar ist das Correlation hinzugefügt wird, combine verwenden
        # TODO maybe throw exception if value exists more than once
        # try finding value
        pass

    def add_correlations(self, correlations: list[MispCorrelation]) -> bool:
        # überprüfen ob correlation schon da
        pass

    def add_over_correlating_value(self, value: str, count: int) -> bool:
        # überprüfen ob correlation schon da
        pass

    def delete_over_correlating_value(self, value: str) -> bool:

        pass

    def delete_correlations(self, value: str) -> bool:
        # correlation_values löschen
        # dann einträge aus default correlation löschen
        pass
