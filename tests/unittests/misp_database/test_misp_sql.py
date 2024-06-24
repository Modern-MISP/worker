from unittest import TestCase

from mmisp.db.models.correlation import OverCorrelatingValue, CorrelationValue, DefaultCorrelation
from sqlalchemy import delete
from sqlmodel import Session, select

from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.db.models.attribute import Attribute
from mmisp.worker.misp_dataclasses.misp_minimal_event import MispMinimalEvent
from mmisp.api_schemas.galaxies import GetGalaxyClusterResponse
from mmisp.db.models.post import Post


class TestMispSQL(TestCase):
    """ "
    Set following environment variables for the tests:
    MMISP_DB_SQL_DBMS=mysql;MMISP_DB_SQL_USER=misp02;MMISP_DB_SQL_PORT=3306;MMISP_DB_SQL_PASSWORD=JLfvs844fV39q6jwG1DGTiZPNjrz6N7W;MMISP_DB_SQL_HOST=db.mmisp.cert.kit.edu;MMISP_DB_SQL_DATABASE=misp02
    """

    misp_sql: MispSQL = MispSQL()

    def __get_test_correlation(self) -> DefaultCorrelation:
        return DefaultCorrelation(
            attribute_id=10000,
            object_id=1,
            event_id=3,
            org_id=65,
            distribution=65,
            object_distribution=65,
            event_distribution=65,
            sharing_group_id=65,
            object_sharing_group_id=65,
            event_sharing_group_id=65,
            attribute_id_1=20000,
            object_id_1=65,
            event_id_1=65,
            org_id_1=65,
            distribution_1=65,
            object_distribution_1=65,
            event_distribution_1=65,
            sharing_group_id_1=65,
            object_sharing_group_id_1=65,
            event_sharing_group_id_1=65,
        )

    def __get_test_cluster(self, blocked: bool) -> GetGalaxyClusterResponse:
        if blocked:
            return GetGalaxyClusterResponse(
                id=44,
                uuid="129e7ee1-9949-4d86-a27e-623d8e5bdde0",
                authors=[],
                distribution=66,
                default=False,
                locked=False,
                published=False,
                deleted=False,
                galaxy_id=66,
            )

        return GetGalaxyClusterResponse(
            id=43,
            uuid="dfa2eeeb-6b66-422d-b146-94ce51de90a1",
            authors=[],
            distribution=66,
            default=False,
            locked=False,
            published=False,
            deleted=False,
            galaxy_id=66,
        )

    def __get_test_minimal_events(self) -> list[MispMinimalEvent]:
        response: list[MispMinimalEvent] = []
        response.append(
            MispMinimalEvent(
                id=1,
                timestamp=0,
                published=False,
                uuid="00c086f7-7524-444c-8bf0-834a4179750a",
                org_c_uuid="00000000-0000-0000-0000-000000000000",
            )
        )  # is blocked
        response.append(
            MispMinimalEvent(
                id=2,
                timestamp=0,
                published=False,
                uuid="fb2fa4a2-66e5-48a3-9bdd-5c5ce78e11e8",
                org_c_uuid="00000000-0000-0000-0000-000000000000",
            )
        )  # is not blocked
        response.append(
            MispMinimalEvent(
                id=3,
                timestamp=0,
                published=False,
                uuid="00000000-0000-0000-0000-000000000000",
                org_c_uuid="58d38339-7b24-4386-b4b4-4c0f950d210f",
            )
        )  # org blocked
        return response

    def test_get_api_authkey(self):
        expected: str = "b4IeQH4n8D7NEwfsNgVU46zgIJjZjCpjhQFrRzwo"
        result: str = self.misp_sql.get_api_authkey(1)
        self.assertEqual(expected, result)

    def test_filter_blocked_events(self):
        events: list[MispMinimalEvent] = self.__get_test_minimal_events()
        result: list[MispMinimalEvent] = self.misp_sql.filter_blocked_events(events, True, True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 2)

    def test_filter_blocked_clusters(self):
        clusters: list[GetGalaxyClusterResponse] = [self.__get_test_cluster(True), self.__get_test_cluster(False)]
        result: list[GetGalaxyClusterResponse] = self.misp_sql.filter_blocked_clusters(clusters)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 43)

    def test_get_attributes_with_same_value(self):
        result: list[Attribute] = self.misp_sql.get_attributes_with_same_value("test")
        for attribute in result:
            self.assertEqual("test", attribute.value1)

    def test_get_values_with_correlation(self):
        result: list[str] = self.misp_sql.get_values_with_correlation()
        with Session(self.misp_sql._engine) as session:
            quality: int = 0
            for value in result:
                statement = select(CorrelationValue.value).where(CorrelationValue.value == value)
                result_search: str = session.exec(statement).first()
                self.assertEqual(result_search, value)
                quality += 1
                if quality > 10:
                    break
        is_there: bool = "test_misp_sql_c" in result
        self.assertTrue(is_there)

    def test_get_over_correlating_values(self):
        result: list[tuple[str, int]] = self.misp_sql.get_over_correlating_values()
        for value in result:
            check: bool = self.misp_sql.is_over_correlating_value(value[0])
            self.assertTrue(check)
            self.assertGreater(value[1], 0)
        is_there: bool = ("Turla", 34) in result
        self.assertTrue(is_there)

    def test_get_excluded_correlations(self):
        result: list[str] = self.misp_sql.get_excluded_correlations()
        for value in result:
            check: bool = self.misp_sql.is_excluded_correlation(value)
            self.assertTrue(check)
        is_there: bool = "test_misp_sql" in result
        self.assertTrue(is_there)

    def test_get_threat_level(self):
        result1: str = self.misp_sql.get_threat_level(1)
        self.assertEqual(result1, "High")

        result2: str = self.misp_sql.get_threat_level(2)
        self.assertEqual(result2, "Medium")

        result3: str = self.misp_sql.get_threat_level(3)
        self.assertEqual(result3, "Low")

        result4: str = self.misp_sql.get_threat_level(4)
        self.assertEqual(result4, "Undefined")

        result5: str = self.misp_sql.get_threat_level(5)
        self.assertIsNone(result5)

    def test_get_post(self):
        expected: Post = Post(
            id=1,
            date_created="2023-11-16 00:33:46",
            date_modified="2023-11-16 00:33:46",
            user_id=1,
            contents="my comment",
            post_id=0,
            thread_id=1,
        )
        post: Post = self.misp_sql.get_post(1)
        self.assertEqual(post.id, expected.id)
        self.assertEqual(post.user_id, expected.user_id)
        self.assertEqual(post.contents, expected.contents)
        self.assertEqual(post.post_id, expected.post_id)
        self.assertEqual(post.thread_id, expected.thread_id)

        not_post: Post = self.misp_sql.get_post(100)
        self.assertIsNone(not_post)

    def test_is_excluded_correlation(self):
        result: bool = self.misp_sql.is_excluded_correlation("1.2.3.4")
        self.assertTrue(result)

        false_result: bool = self.misp_sql.is_excluded_correlation("notthere")
        self.assertFalse(false_result)

    def test_is_over_correlating_value(self):
        result: bool = self.misp_sql.is_over_correlating_value("turla")
        self.assertTrue(result)

        false_result: bool = self.misp_sql.is_over_correlating_value("notthere")
        self.assertFalse(false_result)

    def test_get_number_of_correlations(self):
        over_result: int = self.misp_sql.get_number_of_correlations("Turla", True)
        self.assertEqual(over_result, 34)

        no_result: int = self.misp_sql.get_number_of_correlations("test_misp_sql", False)
        self.assertEqual(no_result, 0)

        normal_result: int = self.misp_sql.get_number_of_correlations("195.22.28.196", False)
        self.assertGreater(normal_result, 0)

    def test_add_correlation_value(self):
        result: int = self.misp_sql.add_correlation_value("test_misp_sql")
        self.assertGreater(result, 0)
        with Session(self.misp_sql._engine) as session:
            statement = select(CorrelationValue).where(CorrelationValue.value == "test_misp_sql")
            search_result: CorrelationValue = session.exec(statement).all()[0]
            self.assertEqual(search_result.value, "test_misp_sql")
            self.assertGreater(search_result.id, 0)

            check_result: int = self.misp_sql.add_correlation_value("test_misp_sql")
            self.assertEqual(check_result, result)

            statement = delete(CorrelationValue).where(CorrelationValue.value == "test_misp_sql")
            session.execute(statement)
            session.commit()

    def test_add_correlations(self):
        not_adding: list[DefaultCorrelation] = [self.__get_test_correlation()]
        not_adding_value: str = "hopefully not in the database :)"
        value_id: int = self.misp_sql.add_correlation_value(not_adding_value)
        not_adding[0].value_id = value_id
        result = self.misp_sql.add_correlations(not_adding)
        self.assertTrue(result)

        not_adding1: list[DefaultCorrelation] = [self.__get_test_correlation()]
        try_again: bool = self.misp_sql.add_correlations(not_adding1)
        self.assertFalse(try_again)

        self.misp_sql.delete_correlations(not_adding_value)

    def test_add_over_correlating_value(self):
        added: bool = self.misp_sql.add_over_correlating_value("test_sql_delete", 66)
        self.assertTrue(added)
        with Session(self.misp_sql._engine) as session:
            statement = select(OverCorrelatingValue).where(OverCorrelatingValue.value == "test_sql_delete")
            result: OverCorrelatingValue = session.exec(statement).all()[0]
            self.assertEqual(result.value, "test_sql_delete")
            self.assertEqual(result.occurrence, 66)
            self.assertGreater(result.id, 0)
        self.misp_sql.delete_over_correlating_value("test_sql_delete")

    def test_delete_over_correlating_value(self):
        self.misp_sql.add_over_correlating_value("test_sql_delete", 66)
        deleted: bool = self.misp_sql.delete_over_correlating_value("test_sql_delete")
        self.assertTrue(deleted)
        with Session(self.misp_sql._engine) as session:
            statement = select(OverCorrelatingValue).where(OverCorrelatingValue.value == "test_sql_delete")
            result: OverCorrelatingValue = session.exec(statement).first()
            self.assertIsNone(result)

        not_there: bool = self.misp_sql.delete_over_correlating_value("test_sql_delete")
        self.assertFalse(not_there)

    def test_delete_correlations(self):
        adding: list[DefaultCorrelation] = [self.__get_test_correlation()]
        value_id: int = self.misp_sql.add_correlation_value("hopefully not in the database :)")
        adding[0].value_id = value_id
        self.misp_sql.add_correlations(adding)
        amount: int = self.misp_sql.get_number_of_correlations("hopefully not in the database :)", False)
        self.assertEqual(1, amount)

        deleted: bool = self.misp_sql.delete_correlations("hopefully not in the database :)")
        self.assertTrue(deleted)

        amount = self.misp_sql.get_number_of_correlations("hopefully not in the database :)", False)
        self.assertEqual(0, amount)

        with Session(self.misp_sql._engine) as session:
            statement = select(CorrelationValue).where(CorrelationValue.value == "hopefully not in the database :)")
            result: CorrelationValue = session.exec(statement).first()
            self.assertIsNone(result)

    def test_get_event_tag_id(self):
        exists = self.misp_sql.get_event_tag_id(3, 6)
        self.assertEqual(exists, 1)
        not_exists = self.misp_sql.get_event_tag_id(1, 100)
        self.assertEqual(not_exists, -1)

    def test_get_attribute_tag_id(self):
        exists = self.misp_sql.get_attribute_tag_id(8, 1)
        self.assertEqual(exists, 1)
        not_exists = self.misp_sql.get_attribute_tag_id(1, 100)
        self.assertEqual(not_exists, -1)
