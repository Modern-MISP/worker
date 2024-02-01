from uuid import UUID

from mmisp.worker.misp_dataclasses.misp_correlation import MispCorrelation, OverCorrelatingValue, CorrelationValue
from mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from mmisp.worker.misp_dataclasses.misp_post import MispPost
from mmisp.worker.misp_dataclasses.misp_sharing_group import MispSharingGroup
from mmisp.worker.misp_dataclasses.misp_sighting import MispSighting
from mmisp.worker.misp_dataclasses.misp_thread import MispThread

from sqlmodel import create_engine, or_, select, Session
from sqlalchemy import Table, MetaData, delete, and_, not_, func


engine = create_engine('mysql+mysqlconnector://misp02:JLfvs844fV39q6jwG1DGTiZPNjrz6N7W@db.mmisp.cert.kit.edu:3306/misp02')
# TODO add real database


class MispSQL:

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
        """
        Get all blocked events from database and remove them from events list. Also if the org is blocked, the
        events in the org are removed from the list. Return the list without the blocked events.
        :param events: list to remove blocked events from
        :type events: list[MispEvent]
        :param use_event_blocklist: if True, blocked events are removed from the list
        :type use_event_blocklist: bool
        :param use_org_blocklist: if True, the events from blocked orgs are removed from the list
        :type use_org_blocklist: bool
        :return: the list without the blocked events
        :rtype: list[MispEvent]
        """
        with Session(engine) as session:
            if use_org_blocklist:
                blocked_table = Table('org_blocklists', MetaData(), autoload_with=engine)
                for event in events:
                    statement = select(blocked_table).where(blocked_table.c.org_uuid == event.org_uuid)
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
            return events


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
        """
        Method to get all attributes with the same value from database.
        :param value: to get attributes with
        :type value: str
        :return: list of attributes with the same value
        :rtype: list[MispEventAttribute]
        """
        with Session(engine) as session:
            statement = select(MispEventAttribute).where(or_(MispEventAttribute.value1 == value,
                                                         MispEventAttribute.value2 == value))
            result: list[MispEventAttribute] = session.exec(statement).all()
            return result

    def get_values_with_correlation(self) -> list[str]:
        """"
        Method to get all values from correlation_values table.
        :return: all values from correlation_values table
        :rtype: list[str]
        """
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
            statement = select(OverCorrelatingValue.value, OverCorrelatingValue.occurrence)
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
        """
        Method to get a thread from database.
        :param thread_id: the id of the thread to get
        :type thread_id: str
        :return: the thread with the given id
        :rtype: MispThread
        """
        with Session(engine) as session:
            statement = select(MispThread).where(MispThread.id == thread_id)
            result: MispThread = session.exec(statement).first()
            return result

    def get_post(self, post_id: int) -> MispPost:
        """
        Method to get a post from database.
        :param post_id: the id of the post to get
        :type post_id: int
        :return: the post with the given id
        :rtype: MispPost
        """
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
            statement = select(OverCorrelatingValue).where(OverCorrelatingValue.value == value)
            result = session.exec(statement).all()
            if len(result) == 0:
               return False
            else:
                return True


    def get_number_of_correlations(self, value: str, only_correlation_table: bool) -> int:
        """
        Returns the number of correlations of value in the database. If only_correlation_table is True, only the
        value in the over_correlating_values table is returned. Else the number of  correlations in the
        default_correlations table is returned
        :param value: to get number of correlations of
        :type value: str
        :param only_correlation_table: if True, only the value in the over_correlating_values table is returned
        :type only_correlation_table: bool
        :return: number of correlations of value in the database
        """
        if only_correlation_table:
            statement = select(OverCorrelatingValue.occurrence).where(OverCorrelatingValue.value == value)
            result: int = session.exec(statement).first()
            return result
        search_statement = select(CorrelationValue.id).where(CorrelationValue.value == value)
        value_id: int = session.exec(search_statement)
        if value_id:
            statement = select(func.count(MispCorrelation)).where(MispCorrelation.value_id == value_id)
            number: int = session.exec(statement)
            return number

    def add_correlation_value(self, value: str) -> int:
        """
        Adds a new value to correlation_values table or returns the id of the current entry with the same value.
        :param value: to add or get id of in the correlation_values table
        :type value: str
        :return: the id of the value in the correlation_values table
        :rtype: int
        """
        with Session(engine) as session:
            statement = select(CorrelationValue).where(CorrelationValue.value == value)
            result: CorrelationValue = session.exec(statement).first()
            if len(result) == 0:
                new_value: CorrelationValue = CorrelationValue(value=value)
                session.add(new_value)
                session.commit()
                session.refresh(new_value)
                return new_value.id
            else:
                return result.id

    def add_correlations(self, correlations: list[MispCorrelation]) -> bool:
        """
        Adds a list of correlations to the database. Returns True if at least one correlation was added, False otherwise.
        Doesn't add correlations that are already in the database.
        :param correlations: list of correlations to add
        :type correlations: list[MispCorrelation]
        :return: true if at least one correlation was added, false otherwise
        :rtype: bool
        """
        changed: bool = False
        with Session(engine) as session:
            for correlation in correlations:
                search_statement = select(MispCorrelation).where(or_(and_(MispCorrelation.attribute_id == correlation.attribute_id,
                                                                        MispCorrelation.attribute_id_1 == correlation.attribute_id_1),
                                                                     and_(MispCorrelation.attribute_id == correlation.attribute_id_1,
                                                                        MispCorrelation.attribute_id_1 == correlation.attribute_id)))
                search_result = session.exec(search_statement).first()
                if search_result:
                    continue
                session.add(correlation)
                changed = True
            session.commit()
            return changed

    def add_over_correlating_value(self, value: str, count: int) -> bool:
        """
        Adds a new value to over_correlating_values table or updates the current entry with the same value.
        Returns True if value was added or updated, False otherwise.
        :param value: add or update
        :type value: str
        :param count: occurrence of value
        :type count: int
        :return: True if value was added or updated, False otherwise
        :rtype: bool
        """
        with Session(engine) as session:
            statement = select(OverCorrelatingValue).where(OverCorrelatingValue.value == value)
            result = session.exec(statement).first()
            if result:
                result.occurrence = count
                session.add(result)
                session.commit()
            else:
                session.add(OverCorrelatingValue(value=value, occurrence=count))
                session.commit()
        return True

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
                statement = delete(OverCorrelatingValue).where(table.c.value == value)
                session.exec(statement)
                session.commit()
                return True
        return False


    def delete_correlations(self, value: str) -> bool:
        """
        Deletes all correlations with value from database. Returns True if value was in database, False otherwise.
        :param value: to delete the correlations of
        :type value: str
        :return: True if value was in database, False otherwise
        :rtype: bool
        """
        with Session(engine) as session:
            value_table = Table('correlation_values', MetaData(), autoload_with=engine)
            statement_value_id = select(value_table.c.id).where(value_table.c.value == value)
            value_id: int = session.exec(statement_value_id).first()

            if value_id:
                delete_statement_value = delete(value_table).where(value_table.c.value == value)
                session.exec(delete_statement_value)

                delete_statement_correlations = delete(MispCorrelation).where(MispCorrelation.value_id == value_id)
                session.exec(delete_statement_correlations)

                session.commit()
                return True
            else:
                return False
