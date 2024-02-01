import unittest

from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import CVETypeValidator
from mmisp.worker.misp_dataclasses.attribute_type import AttributeType


class CVETestcase(unittest.TestCase):

    def test_validate_CVE(self):

        test_dictionary = [
            {'from': 'cve-2021-1234', 'to': AttributeType(types=['vulnerability'], default_type='vulnerability',
                                                          value="CVE-2021-1234")},  # valid
            {'from': 'CVE-2019-56789', 'to': AttributeType(types=['vulnerability'], default_type='vulnerability',
                                                          value="CVE-2019-56789")},  # valid
            {'from': 'cVe-2020-9876543', 'to': AttributeType(types=['vulnerability'], default_type='vulnerability',
                                                          value="CVE-2020-9876543")},  # valid
            {'from': 'cve-2018-54321', 'to': AttributeType(types=['vulnerability'], default_type='vulnerability',
                                                          value="CVE-2018-54321")},  # valid
            {'from': 'CVE-2017-123456789', 'to': AttributeType(types=['vulnerability'], default_type='vulnerability',
                                                          value="CVE-2017-123456789")},  # valid
            {'from': 'cve-12345', 'to': None},  # invalid
            {'from': 'CVE-ABCDE', 'to': None},  # invalid
            {'from': 'CVE-2022-12345-67890', 'to': None},  # invalid
            {'from': 'cve-ABCD-5678', 'to': None}  # invalid
        ]
        for testcase in test_dictionary:
            result = CVETypeValidator().validate(testcase["from"])
            self.assertEqual(result, testcase["to"])



if __name__ == '__main__':
    unittest.main()
