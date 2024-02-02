import unittest
import time
from email_validator import validate_email

from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import EmailTypeValidator
from mmisp.worker.misp_dataclasses.attribute_type import AttributeType


class ASTestcase(unittest.TestCase):

    def test_validate_AS(self):
        test_dictionary = [
            {'from': 'john.doe@gmail.com', 'to': True},  # valid
            {'from': 'alice_smith123@gmail.com', 'to': True},  # valid
            {'from': 'contact@company.org', 'to': True},  # valid
            {'from': 'info+support@website.net', 'to': True},  # valid
            {'from': 'user123@domain-name.co.uk', 'to': True},  # invalid
            {'from': 'john.doe@example', 'to': False},  # invalid
            {'from': '@gmail.com', 'to': False},  # valid
            {'from': 'user123@', 'to': False},  # invalid
            {'from': 'invalid-email@.org ', 'to': False}  # invalid
        ]
        for testcase in test_dictionary:
            start_time = time.time()
            result = EmailTypeValidator().validate(testcase["from"])
            print(testcase["from"], ":", time.time() - start_time)
            if testcase["to"]:
                self.assertEqual(result,  AttributeType(types=['email', 'email-src', 'email-dst', 'target-email', 'whois-registrant-email'],
                  default_type='email-src', value=testcase["from"]))
            else:
                self.assertEqual(result, None)


if __name__ == '__main__':
    unittest.main()
