from uuid import UUID

from mmisp.worker.misp_dataclasses.misp_correlation import MispCorrelation
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from mmisp.worker.misp_dataclasses.misp_post import MispPost
from mmisp.worker.misp_dataclasses.misp_proposal import MispProposal
from mmisp.worker.misp_dataclasses.misp_sharing_group import MispSharingGroup
from mmisp.worker.misp_dataclasses.misp_sighting import MispSighting
from mmisp.worker.misp_dataclasses.misp_tag import MispTag
from mmisp.worker.misp_dataclasses.misp_thread import MispThread

from sqlmodel import create_engine, or_, select, Session
from sqlalchemy import Table, MetaData, delete, and_, not_


engine = create_engine('mysql+mysqlconnector://misp02:JLfvs844fV39q6jwG1DGTiZPNjrz6N7W@db.mmisp.cert.kit.edu:3306/misp02')
# TODO add real database


class MispSQL:


    def get_galaxy_clusters(self, param: str) -> list[MispGalaxyCluster]:
        # braucht ahmad doch nicht
        pass

    def get_event_ids(self, param: str) -> list[int]:
        # braucht ahmad doch nicht
        pass

    def get_tags(self, param: str) -> list[MispTag]:
        # braucht ahmad doch nicht
        pass

    def get_sharing_groups(self) -> list[MispSharingGroup]:
        """
        Method to get all sharing groups from database. None if there are no sharing groups.
        :return: all sharing groups from database
        :rtype: list[MispSharingGroup]
        """
        with Session(engine) as session:
            statement = select(MispSharingGroup)
            result: list[MispSharingGroup] = session.exec(statement).all()
            return result

    def filter_blocked_events(self, events: list[MispEvent], use_event_blocklist: bool, use_org_blocklist: bool) \
            -> list[MispEvent]:
        with Session(engine) as session:
            if use_org_blocklist:
                blocked_table = Table('org_blocklists', MetaData(), autoload_with=engine)
                for event in events:
                    statement = select(blocked_table).where(blocked_table.c.org_id == event.org_id)
                    result = session.exec(statement).all()
                    if len(result) > 0:
                        events.remove(event)
            if use_event_blocklist:
                blocked_table = Table('event_blocklists', MetaData(), autoload_with=engine)
                for event in events:
                    statement = select(blocked_table).where(blocked_table.c.event_uuid == event.uuid)
                    result = session.exec(statement).all()
                    if len(result) > 0:
                        events.remove(event)


    def filter_blocked_clusters(self, clusters: list[MispGalaxyCluster]) -> list[MispGalaxyCluster]:
        """
        Didnt check if works!!!
        Get all blocked clusters from database and remove them from clusters list.
        :param clusters: list of clusters to check
        :type clusters: list[MispGalaxyCluster]
        :return: list without blocked clusters
        :rtype: list[MispGalaxyCluster]
        """
        with Session(engine) as session:
            blocked_table = Table('galaxy_cluster_blocklists', MetaData(), autoload_with=engine)
            for cluster in clusters:
               statement = select(blocked_table).where(blocked_table.c.cluster_uuid == cluster.uuid)
               result = session.exec(statement).all()
               if len(result) > 0:
                  clusters.remove(cluster)
            return clusters

    def get_attributes_with_same_value(self, value: str) -> list[MispEventAttribute]:
        with Session(engine) as session:
            statement = select(MispEventAttribute).where(or_(MispEventAttribute.value1 == value,
                                                         MispEventAttribute.value2 == value))
            result: list[MispEventAttribute] = session.exec(statement).all()
            return result

    def get_values_with_correlation(self) -> list[str]:
        with Session(engine) as session:
            table = Table('correlation_values', MetaData(), autoload_with=engine)
            statement = select(table.c.value)
            result: list[str] = session.exec(statement).all()
            return result

    def get_over_correlating_values(self) -> list[tuple[str, int]]:
        """
        Method to get all values from over_correlating_values table with their occurrence.
        :return: all values from over_correlating_values table with their occurrence
        :rtype: list[tuple[str, int]]
        """
        with Session(engine) as session:
            table = Table('over_correlating_values', MetaData(), autoload_with=engine)
            statement = select(table.c.value, table.c.occurrence)
            result: list[tuple[str, int]]  = session.exec(statement).all()
            return result

    def get_excluded_correlations(self) -> list[str]:
        """
        Method to get all values from correlation_exclusions table.
        :return: all values from correlation_exclusions table
        :rtype: list[str]
        """
        with Session(engine) as session:
            table = Table('correlation_exclusions', MetaData(), autoload_with=engine)
            statement = select(table.c.value)
            result = session.exec(statement).all()
            return result

    def get_thread(self, thread_id: str) -> MispThread:
        with Session(engine) as session:
            statement = select(MispThread).where(MispThread.id == thread_id)
            result: MispThread = session.exec(statement).first()
            return result

    def get_post(self, post_id: int) -> MispPost:
        with Session(engine) as session:
            statement = select(MispPost).where(MispPost.id == post_id)
            result: MispPost = session.exec(statement).first()
            return result

    def is_excluded_correlation(self, value: str) -> bool:
        """
        Checks if value is in correlation_exclusions table.
        :param value: to check
        :type value: str
        :return: True if value is in correlation_exclusions table, False otherwise
        :rtype: bool
        """
        with Session(engine) as session:
            table = Table('correlation_exclusions', MetaData(), autoload_with=engine)
            statement = select(table).where(table.c.value == value)
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
        with Session(engine) as session:
            table = Table('over_correlating_values', MetaData(), autoload_with=engine)
            statement = select(table).where(table.c.value == value)
            result = session.exec(statement).all()
            if len(result) == 0:
               return False
            else:
                return True

    def save_proposal(self, proposal: MispProposal) -> bool:
        # braucht ahmad doch nicht
        pass

    def save_sighting(self, sighting: MispSighting) -> bool:
        # braucht ahmad doch nicht
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
        """
        Deletes value from over_correlating_values table. Returns True if value was in table, False otherwise.
        :param value: row to delete
        :type value: str
        :return: true if value was in table, false otherwise
        :rtype: bool
        """
        result = self.is_over_correlating_value(value)
        if result:
            with Session(engine) as session:
                table = Table('over_correlating_values', MetaData(), autoload_with=engine)
                statement = delete(table).where(table.c.value == value)
                session.exec(statement)
                session.commit()
                return True
        return False


    def delete_correlations(self, value: str) -> bool:
        # correlation_values löschen
        # dann einträge aus default correlation löschen
        with Session(engine) as session:
            pass
