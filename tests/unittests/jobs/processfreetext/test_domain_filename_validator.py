import unittest

from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import DomainFilenameTypeValidator
from mmisp.worker.misp_dataclasses.attribute_type import AttributeType


class BTCTestcase(unittest.TestCase):

    def test_validate_domain_filename(self):
        result_dictionary = {
            'hostname': AttributeType(types=['hostname', 'domain', 'url', 'filename'], default_type='hostname',
                                             value=''),
            'domain': AttributeType(types=['domain', 'filename'], default_type='domain',
                                             value=''),
            'link'  : AttributeType(types=['link'], default_type='link', value=''),
            'url'   :  AttributeType(types=['url'], default_type='url', value=''),
            'filename': AttributeType(types=['filename'], default_type='filename', value= ''),
            'regkey': AttributeType(types=['regkey'], default_type='regkey', value='')
        }

        test_dictionary = [
            {'from': 'test.example.com', 'to': 'hostname'},  # valid
            {'from': 'test.com', 'to':  'domain'},  # valid
            {'from': 'https://www.example.com/test', 'to': False},  # valid
            {'from': 'https://www.example.com/test?param1=value1&param2=value2', 'to': False},  # valid
            {'from': 'https://virustotal.com', 'to': False},  # valid
            {'from': 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion', 'to': 'regkey'},  # valid
            {'from': 'tb1qrp33g0q5c7l4r2zn73rkf6g8e8ple4x9ek9hz9@', 'to': False},
            {'from': 'invalid_address', 'to': False},
            {'from': '2A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', 'to': False},
            {'from': 'bc1invalidaddress', 'to': False}
        ]
        for testcase in test_dictionary:
            result = DomainFilenameTypeValidator().validate(testcase["from"])
            print(testcase["from"],"        ",result)
            if testcase["to"]:
                result_dictionary[testcase["to"]].value = testcase["from"]
                self.assertEqual(result, result_dictionary[testcase["to"]])
            #else:
             #   self.assertEqual(result, None)

    def test_validate_is_link(self):

        print(DomainFilenameTypeValidator()._is_link('https://virustotal.com'))

if __name__ == '__main__':
    unittest.main()
