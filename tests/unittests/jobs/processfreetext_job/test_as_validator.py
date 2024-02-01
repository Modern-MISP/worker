import unittest

from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import ASTypeValidator
from mmisp.worker.misp_dataclasses.attribute_type import AttributeType


class ASTestcase(unittest.TestCase):

    def test_validate_AS(self):
        test_dictionary = [
            {'from': 'as123', 'to': AttributeType(types=['AS'], default_type='AS', value='AS123')},  # valid
            {'from': 'aS456', 'to': AttributeType(types=['AS'], default_type='AS', value="AS456")},  # invalid
            {'from': 'bs789', 'to': None},  # invalid
            {'from': 'asxyz', 'to': None},  # invalid
            {'from': 'as', 'to': None},  # invalid
            {'from': 'as@123@', 'to': None},  # invalid
            {'from': 'as789', 'to': AttributeType(types=['AS'], default_type='AS', value="AS789")},  # valid
            {'from': 'ASxyz456', 'to': None},  # invalid
            {'from': 'aS789@xyz', 'to': None}  # invalid
        ]
        for testcase in test_dictionary:
            result = ASTypeValidator().validate(testcase['from'])
            self.assertEqual(result, testcase["to"])


if __name__ == '__main__':
    unittest.main()
