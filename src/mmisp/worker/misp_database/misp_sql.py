from typing import Self, Sequence

from sqlalchemy import Engine, MetaData, Table, and_, delete, select
from sqlmodel import Session, create_engine, or_

from mmisp.api_schemas.galaxies import GetGalaxyClusterResponse
from mmisp.db.models.attribute import Attribute, AttributeTag
from mmisp.db.models.blocklist import EventBlocklist, GalaxyClusterBlocklist, OrgBlocklist
from mmisp.db.models.correlation import (
    CorrelationExclusions,
    CorrelationValue,
    DefaultCorrelation,
    OverCorrelatingValue,
)
from mmisp.db.models.event import EventTag
from mmisp.db.models.post import Post
from mmisp.db.models.server import Server
from mmisp.worker.misp_database.misp_sql_config import misp_sql_config_data
from mmisp.worker.misp_dataclasses.misp_minimal_event import MispMinimalEvent


class MispSQL:
    """
    The class to interact with the MISP SQL database.
    """

    _SQL_DRIVERS: dict[str, str] = {"mysql": "mysqlconnector", "mariadb": "mysqlconnector", "postgresql": "psycopg2"}
    """The Python SQL drivers for the different DBMS."""

    _sql_dbms: str = misp_sql_config_data.dbms
    """The DBMS of the MISP SQL database."""
    _sql_host: str = misp_sql_config_data.host
    """The host of the MISP SQL database."""
    _sql_port: int = misp_sql_config_data.port
    """The port of the MISP SQL database."""
    _sql_user: str = misp_sql_config_data.user
    """The user of the MISP SQL database."""
    _sql_password: str = misp_sql_config_data.password
    """The password of the MISP SQL database."""
    _sql_database: str = misp_sql_config_data.database
    """The database name of the MISP SQL database."""

    _engine: Engine = create_engine(
        f"{_sql_dbms}+{_SQL_DRIVERS[_sql_dbms]}://{_sql_user}:{_sql_password}@{_sql_host}:{_sql_port}/{_sql_database}"
    )
    """The SQLAlchemy engine to connect to the MISP SQL database."""

    def get_api_authkey(self: Self, server_id: int) -> str:
        """
        Method to get the API authentication key of the server with the given ID.
        :param server_id: The ID of the server.
        :type server_id: int
        :return: The API authentication key of the server.
        :rtype: str
        """
        with Session(self._engine) as session:
            statement = select(Server.authkey).where(Server.id == server_id)
            result: str = session.execute(statement).first().decode()
            return result

    def filter_blocked_events(
            self: Self, events: list[MispMinimalEvent], use_event_blocklist: bool, use_org_blocklist: bool
    ) -> list[MispMinimalEvent]:
        """
        Clear the list from events that are listed as blocked in the misp database. Also, if the org is blocked, the
        events in the org are removed from the list. Return the list without the blocked events.
        :param events: list to remove blocked events from
        :type events: list[AddEditGetEventDetails]
        :param use_event_blocklist: if True, blocked events are removed from the list
        :type use_event_blocklist: bool
        :param use_org_blocklist: if True, the events from blocked orgs are removed from the list
        :type use_org_blocklist: bool
        :return: the list without the blocked events
        :rtype: list[MispEvent]
        """
        with Session(self._engine) as session:
            if use_org_blocklist:
                for event in events:
                    statement = select(EventBlocklist).where(OrgBlocklist.org_uuid == event.org_c_uuid)
                    result = session.exec(statement).all()
                    if len(result) > 0:
                        events.remove(event)
            if use_event_blocklist:
                for event in events:
                    statement = select(EventBlocklist).where(EventBlocklist.event_uuid == event.uuid)
                    result = session.exec(statement).all()
                    if len(result) > 0:
                        events.remove(event)
            return events

    def filter_blocked_clusters(self: Self, clusters: list[GetGalaxyClusterResponse]) -> list[GetGalaxyClusterResponse]:
        """
        Get all blocked clusters from database and remove them from clusters list.
        :param clusters: list of clusters to check
        :type clusters: list[GetGalaxyClusterResponse]
        :return: list without blocked clusters
        :rtype: list[MispGalaxyCluster]
        """
        with Session(self._engine) as session:
            for cluster in clusters:
                statement = select(GalaxyClusterBlocklist).where(GalaxyClusterBlocklist.cluster_uuid == cluster.uuid)
                result = session.exec(statement).all()
                if len(result) > 0:
                    clusters.remove(cluster)
            return clusters

    def get_attributes_with_same_value(self: Self, value: str) -> list[Attribute]:
        """
        Method to get all attributes with the same value from database.
        :param value: to get attributes with
        :type value: str
        :return: list of attributes with the same value
        :rtype: list[Attribute]
        """
        with Session(self._engine) as session:
            statement = select(Attribute).where(
                and_(or_(Attribute.value1 == value, Attribute.value2 == value), Attribute.disable_correlation == 0)
            )
            result: list[Attribute] = list(session.exec(statement).all())  # todo: check if this is correct with tests
            sensitive_result = list(filter(lambda x: x.value1 == value or x.value2 == value, result))
            return sensitive_result

    def get_values_with_correlation(self: Self) -> list[str]:
        """ "
        Method to get all values from correlation_values table.
        :return: all values from correlation_values table
        :rtype: list[str]
        """
        with Session(self._engine) as session:
            statement = select(CorrelationValue.value)
            result: Sequence = session.exec(statement).all()
            return list(result)  # todo: check if this is correct with tests

    def get_over_correlating_values(self: Self) -> list[tuple[str, int]]:
        """
        Method to get all values from over_correlating_values table with their occurrence.
        :return: all values from over_correlating_values table with their occurrence
        :rtype: list[tuple[str, int]]
        """
        with Session(self._engine) as session:
            statement = select(OverCorrelatingValue.value, OverCorrelatingValue.occurrence)
            result: Sequence = session.exec(statement).all()
            return list(result)  # todo: check if this is correct with tests

    def get_excluded_correlations(self: Self) -> list[str]:
        """
        Method to get all values from correlation_exclusions table.
        :return: all values from correlation_exclusions table
        :rtype: list[str]
        """
        with Session(self._engine) as session:
            statement = select(CorrelationExclusions.value)
            result: Sequence = session.exec(statement).all()
            return list(result)

    def get_threat_level(self: Self, threat_level_id: int) -> str:
        with Session(self._engine) as session:
            table = Table("threat_levels", MetaData(), autoload_with=self._engine)
            statement = select(table.c.name).where(table.c.id == threat_level_id)
            result: str = session.exec(statement).first()
            if result:
                return result[0]
            return "No threat level found"

    def get_post(self: Self, post_id: int) -> Post:
        """
        Method to get a post from database.
        :param post_id: the id of the post to get
        :type post_id: int
        :return: the post with the given id
        :rtype: MispPost
        """
        with Session(self._engine) as session:
            statement = select(Post).where(Post.id == post_id)
            result: Post = session.exec(statement).first()
            if result:
                return result[0]
            return result

    def is_excluded_correlation(self: Self, value: str) -> bool:
        """
        Checks if value is in correlation_exclusions table.
        :param value: to check
        :type value: str
        :return: True if value is in correlation_exclusions table, False otherwise
        :rtype: bool
        """
        with Session(self._engine) as session:
            statement = select(CorrelationExclusions.id).where(CorrelationExclusions.value == value)
            result = session.exec(statement).first()
            if result:
                return True
            return False

    def is_over_correlating_value(self: Self, value: str) -> bool:
        """
        Checks if value is in over_correlating_values table. Doesn't check if value has more correlations in the
        database than the current threshold.
        :param value: to check
        :type value: str
        :return: True if value is in over_correlating_values table, False otherwise
        :rtype: bool
        """
        with Session(self._engine) as session:
            statement = select(OverCorrelatingValue).where(OverCorrelatingValue.value == value)
            result: OverCorrelatingValue = session.exec(statement).first()
            if result:
                return True
            return False

    def get_number_of_correlations(self: Self, value: str, only_over_correlating_table: bool) -> int:
        """
        Returns the number of correlations of value in the database. If only_over_correlating_table is True, only the
        value in the over_correlating_values table is returned. Else the number of  correlations in the
        default_correlations table is returned
        Attention: It is assumed that the value is in the over_correlating_values table if only_over_correlating_table
         is True.
        :param value: to get number of correlations of
        :type value: str
        :param only_over_correlating_table: if True, only the value in the over_correlating_values table is returned
        :type only_over_correlating_table: bool
        :return: number of correlations of value in the database
        """
        with Session(self._engine) as session:
            if only_over_correlating_table:
                statement = select(OverCorrelatingValue.occurrence).where(OverCorrelatingValue.value == value)
                result: tuple[int,] = session.exec(statement).first()
                if result:
                    return result[0]
                raise ValueError(f"Value {value} not in over_correlating_values table")
            search_statement = select(CorrelationValue.id).where(CorrelationValue.value == value)
            response: tuple[int,] = session.exec(search_statement).first()
            if response:
                value_id: int = response[0]
                statement = select(DefaultCorrelation.id).where(DefaultCorrelation.value_id == value_id)
                all_elements: Sequence = session.exec(statement).all()
                return len(all_elements)
            else:
                return 0

    def add_correlation_value(self: Self, value: str) -> int:
        """
        Adds a new value to correlation_values table or returns the id of the current entry with the same value.
        :param value: to add or get id of in the correlation_values table
        :type value: str
        :return: the id of the value in the correlation_values table
        :rtype: int
        """
        with Session(self._engine) as session:
            statement = select(CorrelationValue).where(CorrelationValue.value == value)
            result: CorrelationValue = session.exec(statement).first()
            if not result:
                new_value: CorrelationValue = CorrelationValue(value=value)
                session.add(new_value)
                session.commit()
                session.refresh(new_value)
                return new_value.id
            else:
                return result[0].id

    def add_correlations(self: Self, correlations: list[DefaultCorrelation]) -> bool:
        """
        Adds a list of correlations to the database. Returns True if at least one correlation was added,
        False otherwise.
        Doesn't add correlations that are already in the database.
        :param correlations: list of correlations to add
        :type correlations: list[DefaultCorrelation]
        :return: true if at least one correlation was added, false otherwise
        :rtype: bool
        """
        changed: bool = False
        with Session(self._engine) as session:
            for correlation in correlations:
                attribute_id1 = correlation.attribute_id
                attribute_id2 = correlation.attribute_id_1
                search_statement_1 = select(DefaultCorrelation.id).where(
                    and_(
                        DefaultCorrelation.attribute_id == attribute_id1,
                        DefaultCorrelation.attribute_id_1 == attribute_id2,
                    )
                )
                search_statement_2 = select(DefaultCorrelation.id).where(
                    and_(
                        DefaultCorrelation.attribute_id == attribute_id2,
                        DefaultCorrelation.attribute_id_1 == attribute_id1,
                    )
                )
                search_result_1: int = session.exec(search_statement_1).first()
                search_result_2: int = session.exec(search_statement_2).first()

                if search_result_1 or search_result_2:
                    continue
                session.add(correlation)
                changed = True
            session.commit()
            return changed

    def add_over_correlating_value(self: Self, value: str, count: int) -> bool:
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
        with Session(self._engine) as session:
            statement = select(OverCorrelatingValue).where(OverCorrelatingValue.value == value)
            result: OverCorrelatingValue = session.exec(statement).first()
            if result:
                result = result[0]
                result.occurrence = count
                session.add(result)
            else:
                session.add(OverCorrelatingValue(value=value, occurrence=count))
            session.commit()
        return True

    def delete_over_correlating_value(self: Self, value: str) -> bool:
        """
        Deletes value from over_correlating_values table. Returns True if value was in table, False otherwise.
        :param value: row to delete
        :type value: str
        :return: true if value was in table, false otherwise
        :rtype: bool
        """
        result = self.is_over_correlating_value(value)
        if result:
            with Session(self._engine) as session:
                statement = delete(OverCorrelatingValue).where(OverCorrelatingValue.value == value)
                session.execute(statement)
                session.commit()
                return True
        return False

    def delete_correlations(self: Self, value: str) -> bool:
        """
        Deletes all correlations with value from database. Returns True if value was in database, False otherwise.
        :param value: to delete the correlations of
        :type value: str
        :return: True if value was in database, False otherwise
        :rtype: bool
        """
        with Session(self._engine) as session:
            statement_value_id = select(CorrelationValue.id).where(CorrelationValue.value == value)
            value_id: int = session.exec(statement_value_id).first()

            if value_id:
                delete_statement_value = delete(CorrelationValue).where(CorrelationValue.value == value)
                session.execute(delete_statement_value)

                delete_statement_correlations = delete(DefaultCorrelation).where(
                    DefaultCorrelation.value_id == value_id
                )
                session.execute(delete_statement_correlations)

                session.commit()
                return True
            else:
                return False

    def get_event_tag_id(self: Self, event_id: int, tag_id: int) -> int:
        """
        Method to get the ID of the event-tag object associated with the given event-ID and tag-ID.

        :param event_id: The ID of the event.
        :type event_id: int
        :param tag_id: The ID of the tag.
        :type tag_id: int
        :return: The ID of the event-tag object or -1 if the object does not exist.
        :rtype: int
        """

        with Session(self._engine) as session:
            statement = select(EventTag.id).where(and_(EventTag.event_id == event_id, EventTag.tag_id == tag_id))
            search_result: int = session.exec(statement).first()
            if search_result:
                return search_result
            else:
                return -1

    def get_attribute_tag_id(self: Self, attribute_id: int, tag_id: int) -> int:
        """
        Method to get the ID of the attribute-tag object associated with the given attribute-ID and tag-ID.

        :param attribute_id: The ID of the attribute.
        :type attribute_id: int
        :param tag_id: The ID of the tag.
        :type tag_id: int
        :return: The ID of the attribute-tag object or -1 if the object does not exist.
        :rtype: int
        """

        with Session(self._engine) as session:
            statement = select(AttributeTag.id).where(
                and_(AttributeTag.attribute_id == attribute_id, AttributeTag.tag_id == tag_id)
            )
            search_result: int = session.exec(statement).first()
            if search_result:
                return search_result
            else:
                return -1

    def get_attribute_tag(self: Self, attribute_tag_id: int) -> AttributeTag:
        """
        Method to get the AttributeTag object with the given ID.

        :param attribute_tag_id: The ID of the attribute-tag object.
        :type attribute_tag_id: int
        :return: The AttributeTag object.
        :rtype: AttributeTag
        """

        with Session(self._engine) as session:
            statement = select(AttributeTag).where(AttributeTag.id == attribute_tag_id)
            return session.exec(statement).first()
