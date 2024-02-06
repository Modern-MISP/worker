import datetime
import unittest
import uuid
from unittest.mock import Mock, MagicMock
from uuid import UUID

from faker import Faker

from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispSQLEventAttribute, MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_object import MispObject
from mmisp.worker.misp_dataclasses.misp_post import MispPost
from mmisp.worker.misp_dataclasses.misp_thread import MispThread


class MispSQLMock(MagicMock):

    @staticmethod
    def __create_fake_sql_events() -> list[MispSQLEventAttribute]:
        faker: Faker = Faker()
        example_objects: list[MispSQLEventAttribute] = []
        for _ in range(21):
            example_object = MispSQLEventAttribute(
                event_id=faker.pyint(),
                object_id=faker.pyint(),
                object_relation=faker.word()[:6],
                category=faker.word()[:6],
                type=faker.word()[:6],
                value1=faker.bothify(text="overcorrelating"),
                value2=faker.word()[:6],
                to_ids=faker.pybool(),
                uuid=str(uuid.uuid4()),
                timestamp=faker.random_int(),
                distribution=faker.pyint(),
                sharing_group_id=faker.pyint(),
                comment=faker.text()[:255],
                deleted=faker.pybool(),
                disable_correlation=faker.pybool(),
                first_seen=faker.pyint(),
                last_seen=faker.pyint(),
            )
            example_objects.append(example_object)
        for _ in range(5):
            example_object = MispSQLEventAttribute(
                event_id=66,
                object_id=66,
                object_relation=faker.word()[:6],
                category=faker.word()[:6],
                type=faker.word()[:6],
                value1=faker.bothify(text="correlation"),
                value2=faker.word()[:6],
                to_ids=faker.pybool(),
                uuid=str(uuid.uuid4()),
                timestamp=faker.random_int(),
                distribution=faker.pyint(),
                sharing_group_id=faker.pyint(),
                comment=faker.text()[:255],
                deleted=faker.pybool(),
                disable_correlation=faker.pybool(),
                first_seen=faker.pyint(),
                last_seen=faker.pyint(),
            )
            example_objects.append(example_object)
        return example_objects

    values_with_correlation: list[str] = ["correlation", "top1", "top2", "top3", "top4", "top5"]
    over_correlating_values: list[tuple[str, int]] = [("overcorrelating", 25)]
    excluded_correlations: list[str] = ["excluded"]
    sql_event_attributes: list[MispSQLEventAttribute] = __create_fake_sql_events()


    def get_event_tag_id(self, event_id: int, tag_id: int) -> int:
        return 1

    def get_attribute_tag_id(self, attribute_id: int, tag_id: int) -> int:
        if attribute_id == 1 and tag_id == 2:
            return 10
        elif attribute_id == 1 and tag_id == 3:
            return 11
        return 1

    def get_post(self, post_id: int) -> MispPost:
        match post_id:
            case 1: return MispPost(id=1,
                                    date_created="2023 - 11 - 16",
                                    date_modified="2023 - 11 - 16",
                                    user_id=1,
                                    contents="test content",
                                    post_id=1,
                                    thread_id=1)

    def get_thread(self, thread_id: int) -> MispThread:
        match thread_id:
            case 1: return MispThread(id=1, date_created=datetime.datetime(2023, 11, 16, 0, 0),
                                      date_modified=datetime.datetime(2023, 11, 16, 0, 0),
                                      distribution=1, user_id=1, post_count=1, event_id=1, title="test title", org_id=1,
                                      sharing_group_id=1)

    def get_threat_level(self, threat_level_id: int) -> str:
        match threat_level_id:
            case 1: return "high"
            case 2: return "medium"
            case 3: return "low"
            case 4: return "undefined"


    def get_values_with_correlation(self) -> list[str]:
        return self.values_with_correlation

    def get_over_correlating_values(self) -> list[tuple[str, int]]:
        return self.over_correlating_values

    def get_excluded_correlations(self) -> list[str]:
        return self.excluded_correlations

    def is_excluded_correlation(self, value: str) -> bool:
        return value in self.excluded_correlations

    def is_over_correlating_value(self, value: str) -> bool:
        return value in self.over_correlating_values

    def get_attributes_with_same_value(self, value: str) -> list[MispSQLEventAttribute]:
        result: list[MispSQLEventAttribute] = []
        for event in self.sql_event_attributes:
            if event.value1 == value or event.value2 == value:
                result.append(event)
        return result

    def get_number_of_correlations(self, value: str, only_over_correlating_table: bool) -> int:
        if only_over_correlating_table:
            if value == "overcorrelating":
                index: int = self.over_correlating_values.index((value, 25))
                return self.over_correlating_values[index][1]
        return Faker().pyint()

    def add_correlation_value(self, value: str) -> int:
        try:
            index: int = self.values_with_correlation.index(value)
        except ValueError:
            self.values_with_correlation.append(value)
            index = self.values_with_correlation.index(value)
        return index

