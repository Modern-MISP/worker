import unittest

from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import DomainFilenameTypeValidator
from mmisp.worker.misp_dataclasses.attribute_type import AttributeType


class BTCTestcase(unittest.TestCase):

    def test_validate_btc(self):
        result_dictionary = {
            'hostname': True,
            'domain': True,
            'link'  : True,
            'url'   : True,
            'filename': True,
            'regkey': True
        }

        test_dictionary = [
            {'from': 'test.example.com', 'to': 'hostname'},  # valid
            {'from': 'test.com', 'to':  'domain'},  # valid
            {'from': 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion', 'to': True},  # valid
            {'from': 'tb1qrp33g0q5c7l4r2zn73rkf6g8e8ple4x9ek9hz9', 'to': True},  # valid
            {'from': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfN', 'to': True},  # invalid but regex checks
            {'from': 'tb1qrp33g0q5c7l4r2zn73rkf6g8e8ple4x9ek9hz9@', 'to': False},  # valid but @
            {'from': 'invalid_address', 'to': False},  # invalid
            {'from': '2A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', 'to': False},  # invalid
            {'from': 'bc1invalidaddress', 'to': False}  # invalid
        ]
        for testcase in test_dictionary:
            result = DomainFilenameTypeValidator().validate(testcase["from"])
            print(testcase["from"], result)
            #if testcase["to"]:
             #   self.assertEqual(result, AttributeType(types=['btc'], default_type='btc', value=testcase["from"]))
            #else:
             #   self.assertEqual(result, None)


if __name__ == '__main__':
    unittest.main()
