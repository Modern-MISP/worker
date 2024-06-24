import unittest
from typing import Self

from mmisp.worker.jobs.processfreetext.attribute_types.attribute_type import AttributeType
from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import PhonenumberTypeValidator


class PhoneNumberTestcase(unittest.TestCase):
    def test_validate_phone_number(self: Self):
        testcases = ["+1555-123-4567", "+61298765432", "+81312345678", "+81312345678", "123-456-789"]
        for testcase in testcases:
            result = PhonenumberTypeValidator().validate(testcase)
            self.assertEqual(
                result,
                AttributeType(
                    types=["phone-number", "prtn", "whois-registrant-phone"],
                    default_type="phone-number",
                    value=testcase,
                ),
            )

    def test_validate_phone_number_invalid(self: Self):
        testcases = ["+1(0)12345", "12345/67890", "12345/67890/12345"]
        for testcase in testcases:
            result = PhonenumberTypeValidator().validate(testcase)
            self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
