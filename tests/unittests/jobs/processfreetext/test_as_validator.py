import unittest

from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import ASTypeValidator
from mmisp.worker.jobs.processfreetext.attribute_types.attribute_type import AttributeType


class ASTestcase(unittest.TestCase):
    def test_validate_AS(self):
        test_dictionary = ["as123", "aS456", "as789", "aS123", "AS456", "AS789"]
        attribute_type = AttributeType(types=["AS"], default_type="AS", value="")
        for testcase in test_dictionary:
            result = ASTypeValidator().validate(testcase)
            attribute_type.value = testcase.upper()
            self.assertEqual(result, attribute_type)

    def test_validate_AS_invalid(self):
        test_dictionary = ["vs1234", "aS@4567", "as7890@", "AS|1234", "wAS4567", "AS7890a"]
        for testcase in test_dictionary:
            result = ASTypeValidator().validate(testcase)
            self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
