import unittest

from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import DomainFilenameTypeValidator
from mmisp.worker.jobs.processfreetext.attribute_types.attribute_type import AttributeType


class DomainFilenameTestcase(unittest.TestCase):

    def test_validate_hostname(self):
        testcases = ['test.example.com', 'test.example.com:8000']
        for testcase in testcases:
            result = DomainFilenameTypeValidator().validate(testcase)
            if ':' in testcase:
                self.assertEqual(result, AttributeType(types=['hostname', 'domain', 'url', 'filename'], default_type='hostname', value=testcase.split(':')[0]))
            else:
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
        testcases = ['example.txt', 'document.pdf', 'image.jpeg', 'subdomain!.example.com','\\example-file.txt']
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
        testcases = ['example.123:8000', 'my_domain.com!', 'invalid-link']
        for testcase in testcases:
            result = DomainFilenameTypeValidator().validate(testcase)
            self.assertIsNone(result)

    def test_validate_is_link(self):
        self.assertTrue(DomainFilenameTypeValidator()._is_link('https://virustotal.com'))


if __name__ == '__main__':
    unittest.main()
