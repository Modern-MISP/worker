import unittest
from typing import Self

from mmisp.worker.jobs.processfreetext.attribute_types.attribute_type import AttributeType
from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import CVETypeValidator


class CVETestcase(unittest.TestCase):
    def test_validate_CVE(self: Self):
        testcases = ["cve-2021-1234", "cve-2019-56789", "cVe-2020-9876543", "cve-2018-54321", "CVE-2017-123456789"]
        for testcase in testcases:
            result = CVETypeValidator().validate(testcase)
            self.assertEqual(
                result, AttributeType(types=["vulnerability"], default_type="vulnerability", value=testcase.upper())
            )

    def test_validate_invalid_CVE(self: Self):
        testcases = ["cve-12345", "CVE-ABCDE", "CVE-2022-12345-67890", "cve-ABCD-5678"]
        for testcase in testcases:
            result = CVETypeValidator().validate(testcase)
            self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
