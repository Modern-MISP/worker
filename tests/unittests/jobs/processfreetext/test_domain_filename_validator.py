import unittest

from publicsuffix2 import PublicSuffixList

from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import DomainFilenameTypeValidator
from mmisp.worker.misp_dataclasses.attribute_type import AttributeType


class BTCTestcase(unittest.TestCase):

    def test_validate_hostname(self):
        testcases = ['test.example.com']
        for testcase in testcases:
            result = DomainFilenameTypeValidator().validate(testcase)
            self.assertEqual(result, AttributeType(types=['hostname', 'domain', 'url', 'filename'], default_type='hostname', value=testcase))

    def test_validate_domain(self):
        testcases = ['test.com', 'example.com']
        for testcase in testcases:
            result = DomainFilenameTypeValidator().validate(testcase)
            self.assertEqual(result, AttributeType(types=['domain', 'filename'], default_type='domain', value=testcase))

    def test_validate_url(self):
        testcases = ['https://www.example.com/test', 'https://www.example.com/test?param1=value1&param2=value2','ftp://www.example.com']
        for testcase in testcases:
            result = DomainFilenameTypeValidator().validate(testcase)
            self.assertEqual(result, AttributeType(types=['url'], default_type='url', value=testcase))

    def test_validate_filename(self):
        testcases = ['example.txt', 'document.pdf', 'image.jpeg', 'subdomain!.example.com']
        for testcase in testcases:
            result = DomainFilenameTypeValidator().validate(testcase)
            self.assertEqual(result, AttributeType(types=['filename'], default_type='filename', value=testcase))

    def test_validate_regkey(self):
        testcases = ['HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion','HKLM\System\InvalidKey', 'HKCU\Software\KeyWithoutSpaces']
        for testcase in testcases:
            result = DomainFilenameTypeValidator().validate(testcase)
            self.assertEqual(result, AttributeType(types=['regkey'], default_type='regkey', value=testcase))

    def test_validate_link(self):
        testcases = ['https://virustotal.com']
        for testcase in testcases:
            result = DomainFilenameTypeValidator().validate(testcase)
            self.assertEqual(result, AttributeType(types=['link'], default_type='link', value=testcase))

    def test_validate_invalid(self):
        testcases = ['example.123', 'my_domain.com!', 'invalid-link']
        for testcase in testcases:
            result = DomainFilenameTypeValidator().validate(testcase)
            self.assertIsNone(result)

    def test_validate_is_link(self):
        self.assertEqual(DomainFilenameTypeValidator()._is_link('https://virustotal.com'), True)


if __name__ == '__main__':
    unittest.main()
