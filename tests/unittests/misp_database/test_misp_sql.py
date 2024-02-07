import os
from unittest import TestCase, mock

from sqlmodel import Session, select

from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_dataclasses.misp_correlation import OverCorrelatingValue
from mmisp.worker.misp_dataclasses.misp_post import MispPost


class TestMispSQL(TestCase):

    misp_sql: MispSQL = MispSQL()

    def setUp(self):
        url: str = "mysql+mysqlconnector://misp02:JLfvs844fV39q6jwG1DGTiZPNjrz6N7W@db.mmisp.cert.kit.edu:3306/misp02"
        self.misp_sql.set_engine(url)
        super().setUpClass()

    def test_get_galaxy_clusters(self):
        self.fail()

    def test_get_event_ids(self):
        self.fail()

    def test_get_tags(self):
        self.fail()

    def test_get_sharing_groups(self):
        self.fail()

    def test_filter_blocked_events(self):
        self.fail()

    def test_filter_blocked_clusters(self):
        self.fail()

    def test_get_attributes_with_same_value(self):
        self.fail()

    def test_get_values_with_correlation(self):
        self.fail()

    def test_get_over_correlating_values(self):
        self.fail()

    def test_get_excluded_correlations(self):
        self.fail()

    def test_get_thread(self):
        self.fail()

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
        self.fail()

    def test_is_over_correlating_value(self):
        self.fail()

    def test_save_proposal(self):
        self.fail()

    def test_save_sighting(self):
        self.fail()

    def test_get_number_of_correlations(self):
        self.fail()

    def test_add_correlation_value(self):
        self.fail()

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
        exists= self.misp_sql.get_event_tag_id(3, 6)
        self.assertEqual(exists, 1)
        not_exists = self.misp_sql.get_event_tag_id(1, 100)
        self.assertEqual(not_exists, -1)

    def test_get_attribute_tag_id(self):
        exists = self.misp_sql.get_attribute_tag_id(8, 1)
        self.assertEqual(exists, 1)
        not_exists = self.misp_sql.get_attribute_tag_id(1, 100)
        self.assertEqual(not_exists, -1)
