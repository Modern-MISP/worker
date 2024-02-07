import os
from unittest import TestCase, mock

from sqlalchemy import delete
from sqlmodel import Session, select

from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_dataclasses.misp_correlation import OverCorrelatingValue, CorrelationValue
from mmisp.worker.misp_dataclasses.misp_post import MispPost


class TestMispSQL(TestCase):
    """"
    Set following environment variables for the tests:
    MMISP_MISP_SQL_DBMS=mysql;MMISP_MISP_SQL_USER=misp02;MMISP_MISP_SQL_PORT=3306;MMISP_MISP_SQL_PASSWORD=JLfvs844fV39q6jwG1DGTiZPNjrz6N7W;MMISP_MISP_SQL_HOST=db.mmisp.cert.kit.edu;MMISP_MISP_SQL_DATABASE=misp02
    """
    misp_sql: MispSQL = MispSQL()

    def test_get_api_authkey(self):
        expected: str = "b4IeQH4n8D7NEwfsNgVU46zgIJjZjCpjhQFrRzwo"
        result: str = self.misp_sql.get_api_authkey(1)
        self.assertEqual(expected, result)


    def test_filter_blocked_events(self):
        self.fail()

    def test_filter_blocked_clusters(self):
        self.fail()

    def test_get_attributes_with_same_value(self):
        self.fail()

    def test_get_values_with_correlation(self):
        result: list[str] = self.misp_sql.get_values_with_correlation()
        with Session(self.misp_sql.engine) as session:
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
        is_there: bool = ("test_misp_sql", 66) in result
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
        expected: MispPost = MispPost(id=1, date_created="2023-11-16 00:33:46", date_modified="2023-11-16 00:33:46",
                                      user_id=1, contents="my comment", post_id=0, thread_id=1)
        post: MispPost = self.misp_sql.get_post(1)
        self.assertEqual(post.id, expected.id)
        self.assertEqual(post.user_id, expected.user_id)
        self.assertEqual(post.contents, expected.contents)
        self.assertEqual(post.post_id, expected.post_id)
        self.assertEqual(post.thread_id, expected.thread_id)

        not_post: MispPost = self.misp_sql.get_post(100)
        self.assertIsNone(not_post)

    def test_is_excluded_correlation(self):
        result: bool = self.misp_sql.is_excluded_correlation("1.2.3.4")
        self.assertTrue(result)

        false_result: bool = self.misp_sql.is_excluded_correlation("notthere")
        self.assertFalse(false_result)

    def test_is_over_correlating_value(self):
        result: bool = self.misp_sql.is_over_correlating_value("test_misp_sql")
        self.assertTrue(result)

        false_result: bool = self.misp_sql.is_over_correlating_value("notthere")
        self.assertFalse(false_result)

    def test_get_number_of_correlations(self):
        self.fail()

    def test_add_correlation_value(self):
        result: int = self.misp_sql.add_correlation_value("test_misp_sql")
        self.assertGreater(result, 0)
        with Session(self.misp_sql.engine) as session:
            statement = select(CorrelationValue).where(CorrelationValue.value == "test_misp_sql")
            search_result: CorrelationValue = session.exec(statement).all()[0]
            self.assertEqual(search_result.value, "test_misp_sql")
            self.assertGreater(search_result.id, 0)

            check_result: int = self.misp_sql.add_correlation_value("test_misp_sql")
            self.assertEqual(check_result, result)

            statement = delete(CorrelationValue).where(CorrelationValue.value == "test_misp_sql")
            session.exec(statement)
            session.commit()

    def test_add_correlations(self):
        self.fail()

    def test_add_over_correlating_value(self):
        added: bool = self.misp_sql.add_over_correlating_value("test_sql_delete", 66)
        self.assertTrue(added)
        with Session(self.misp_sql.engine) as session:
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
        with Session(self.misp_sql.engine) as session:
            statement = select(OverCorrelatingValue).where(OverCorrelatingValue.value == "test_sql_delete")
            result: OverCorrelatingValue = session.exec(statement).first()
            self.assertIsNone(result)

        not_there: bool = self.misp_sql.delete_over_correlating_value("test_sql_delete")
        self.assertFalse(not_there)

    def test_delete_correlations(self):
        self.fail()

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
