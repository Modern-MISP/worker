import uuid
from typing import Self
from unittest.mock import MagicMock

from faker import Faker

from mmisp.db.models.attribute import Attribute


class MispSQLMock(MagicMock):
    @staticmethod
    def __create_fake_sql_events() -> list[Attribute]:
        faker: Faker = Faker()
        example_objects: list[Attribute] = []
        for _ in range(21):
            example_object = Attribute(
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
            example_object = Attribute(
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
        for _ in range(22):
            example_object = Attribute(
                event_id=faker.pyint(),
                object_id=66,
                object_relation=faker.word()[:6],
                category=faker.word()[:6],
                type=faker.word()[:6],
                value1=faker.bothify(text="new_current"),
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
        for _ in range(25):
            example_object = Attribute(
                event_id=faker.pyint(),
                object_id=66,
                object_relation=faker.word()[:6],
                category=faker.word()[:6],
                type=faker.word()[:6],
                value1=faker.bothify(text="stay"),
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
        example_object = Attribute(
            event_id=69,
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

    def get_event_tag_id(self: Self, event_id: int, tag_id: int) -> int:
        return 1

    def get_attribute_tag_id(self: Self, attribute_id: int, tag_id: int) -> int:
        if attribute_id == 1 and tag_id == 2:
            return 10
        elif attribute_id == 1 and tag_id == 3:
            return 11
        return 1
