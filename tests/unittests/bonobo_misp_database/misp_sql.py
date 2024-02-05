import unittest


class TestMispSQL(unittest.TestCase):

    def test_get_event_tag_id(self, event_id: int, tag_id: int) -> int:
        return 1

    def test_get_attribute_tag_id(self, attribute_id: int, tag_id: int) -> int:
        if attribute_id == 1 and tag_id == 2:
            return 10
        elif attribute_id == 1 and tag_id == 3:
            return 11
        return 1
