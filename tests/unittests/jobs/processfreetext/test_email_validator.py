import unittest

from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import EmailTypeValidator
from mmisp.worker.jobs.processfreetext.attribute_types.attribute_type import AttributeType


class ASTestcase(unittest.TestCase):

    def test_validate_email(self):
        testcases = ['john.doe@gmail.com', 'alice_smith123@gmail.com', 'contact@company.org',
                     'info+support@website.net', 'user123@domain-name.co.uk']
        for testcase in testcases:
            result = EmailTypeValidator().validate(testcase)
            self.assertEqual(result, AttributeType(
                types=['email', 'email-src', 'email-dst', 'target-email', 'whois-registrant-email'],
                default_type='email-src', value=testcase))

    def test_validate_invalid_email(self):
        testcases = ['john.doe@example', '@gmail.com', 'user123@', 'invalid-email@.org ']
        for testcase in testcases:
            result = EmailTypeValidator().validate(testcase)
            self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
