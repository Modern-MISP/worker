import unittest

from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import PhonenumberTypeValidator
from mmisp.worker.misp_dataclasses.attribute_type import AttributeType


class PhoneNumberTestcase(unittest.TestCase):

    def test_validate_phone_number(self):

        test_dictionary = [
            {'from': '+1555-123-4567', 'to': True},  # valid
            {'from': '+61298765432', 'to': True},  # valid
            {'from': '+81312345678', 'to': True},  # valid
            {'from': '+81312345678', 'to': True},  # valid
            {'from': '123-456-789', 'to': True},  # valid
            {'from': '+1(0)12345', 'to': False},  # invalid
            {'from': '12345/67890', 'to': False},  # invalid
            {'from': '12345/67890/12345', 'to': False} # invalid

        ]
        for testcase in test_dictionary:
            result = PhonenumberTypeValidator().validate(testcase["from"])
            print(testcase["from"], ":", result)
            if testcase["to"]:
                self.assertEqual(result, AttributeType(types=['phone-number', 'prtn', 'whois-registrant-phone'],
                                                       default_type='phone-number', value=testcase["from"]))
            else:
                self.assertEqual(result, None)


if __name__ == '__main__':
    unittest.main()
