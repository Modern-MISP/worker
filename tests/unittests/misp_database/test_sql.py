
import unittest

from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_dataclasses.misp_post import MispPost


class MispSQlTest(unittest.TestCase):
    def test_get_post(self):
        try:
            database: MispSQL = MispSQL()
            post: MispPost = database.get_post(19)
            self.assertIsNone(post)
        except Exception as exception:
            print(exception)

    def test_add_over_correlating_value(self):
        #try:
        database: MispSQL = MispSQL()
        result: bool = database.add_over_correlating_value("test", 50)
        self.assertTrue(result)
        #except Exception as exception:
            #print(exception)

