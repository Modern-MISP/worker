import unittest

from publicsuffix2 import PublicSuffixList

from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import DomainFilenameTypeValidator
from mmisp.worker.misp_dataclasses.attribute_type import AttributeType


class BTCTestcase(unittest.TestCase):

    def test_validate_domain_filename(self):
        result_dictionary = {
            'hostname': AttributeType(types=['hostname', 'domain', 'url', 'filename'], default_type='hostname',
                                      value=''),
            'domain': AttributeType(types=['domain', 'filename'], default_type='domain',
                                    value=''),
            'link': AttributeType(types=['link'], default_type='link', value=''),
            'url': AttributeType(types=['url'], default_type='url', value=''),
            'filename': AttributeType(types=['filename'], default_type='filename', value=''),
            'regkey': AttributeType(types=['regkey'], default_type='regkey', value='')
        }

        test_dictionary = [
            {'from': 'test.example.com', 'to': 'hostname'},  # valid
            {'from': 'test.com', 'to': 'domain'},  # valid
            {'from': 'https://www.example.com/test', 'to': 'url'},  # valid
            {'from': 'https://www.example.com/test?param1=value1&param2=value2', 'to': 'url'},  # valid
            {'from': 'https://virustotal.com', 'to': 'link'},  # valid
            {'from': 'example.txt', 'to': 'filename'},  # valid
            {'from': 'document.pdf', 'to': 'filename'},  # valid
            {'from': 'image.jpeg', 'to': 'filename'},  # valid
            {'from': r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion', 'to': 'regkey'},  # valid
            {'from': 'example.123', 'to': False}, # invalid
            {'from': 'subdomain!.example.com', 'to': 'filename'},  # valid
            {'from': 'my_domain.com!', 'to': False},  # invalid
            {'from': 'ftp://www.example.com', 'to': 'url'},  # valid
            {'from': 'htps://sub.example.com', 'to': 'filename'},  # valid
            {'from': 'invalid-link', 'to': False}, # invalid
            {'from': 'my_file%$#.txt', 'to': 'filename'},  # valid
            {'from': 'HKLM\System\InvalidKey', 'to': 'regkey'},  # valid
            {'from': 'HKCU\Software\KeyWithoutSpaces', 'to': 'regkey'},  # valid


        ]
        for testcase in test_dictionary:
            result = DomainFilenameTypeValidator().validate(testcase["from"])
            #print(testcase["from"], "        ", result)
            if testcase["to"]:
                result_dictionary[testcase["to"]].value = testcase["from"]
                self.assertEqual(result, result_dictionary[testcase["to"]])
            else:
               self.assertEqual(result, None)

    def test_validate_is_link(self):
        print(DomainFilenameTypeValidator()._is_link('https://virustotal.com'))


if __name__ == '__main__':
    unittest.main()
