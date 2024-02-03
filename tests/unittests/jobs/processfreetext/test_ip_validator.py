import unittest
import re

from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import IPTypeValidator
from mmisp.worker.misp_dataclasses.attribute_type import AttributeType


class IPTestcase(unittest.TestCase):

    def test_validate_ip(self):
        type_dictionary = {
            'ip': AttributeType(types=['ip-dst', 'ip-src', 'ip-src/ip-dst'], default_type='ip-dst',
                                value=""),
            'ip+port': AttributeType(types=['ip-dst|port', 'ip-src|port', 'ip-src|port/ip-dst|port'],
                                     default_type='ip-dst|port', value=''),
            'cidr': AttributeType(types=['ip-dst', 'ip-src', 'ip-src/ip-dst'], default_type='ip-dst',
                                  value='')
        }
        test_dictionary = [
            {'from': '192.168.1.1', 'to': 'ip', 'value': '192.168.1.1'},  # ipv4
            {'from': '10.0.0.1', 'to': 'ip', 'value': '10.0.0.1'},  # ipv4
            {'from': '172.16.0.1', 'to': 'ip', 'value': '172.16.0.1'},# ipv4
            {'from': '2001:0db8:85a3:0000:0000:8a2e:0370:7334', 'to': 'ip', # ipv6
             'value': '2001:0db8:85a3:0000:0000:8a2e:0370:7334'}, # ipv6
            {"from": "fe80::1%eth0", "to": 'ip', 'value': 'fe80::1%eth0'},  # ipv6
            {'from': '2a00:1450:4007:816::200e', 'to': 'ip', 'value': '2a00:1450:4007:816::200e'}, # ipv6
            {'from': 'fd3e:4f5a:eee4:ffff::1', 'to': 'ip', 'value': 'fd3e:4f5a:eee4:ffff::1'}, # ipv6
            {'from': '192.168.1.1:8080', 'to': 'ip+port', 'value': '192.168.1.1|8080'},  # ipv4+port
            {'from': '10.0.0.1:5000', 'to': 'ip+port', 'value': '10.0.0.1|5000'},  # ipv4+port
            {'from': '[2607:f8b0:4005:080a:0000:0000:0000:200e]:8080', 'to': 'ip+port',
                     'value': '2607:f8b0:4005:080a:0000:0000:0000:200e|8080'},  # ipv6+port
            {'from': '[fd12:3456:789a:1bcd:0000:0000:0000:ef02]:12345', 'to': 'ip+port',
                     'value': 'fd12:3456:789a:1bcd:0000:0000:0000:ef02|12345'},  # ipv6+port
            {"from": "3001:0db8:85a3:0000:0000:8a2e:0370:7334:12345", 'to': 'ip+port',
                     'value': '3001:0db8:85a3:0000:0000:8a2e:0370:7334|12345'},  # ipv6+port
            {'from': '192.168.0.1/24', 'to': 'cidr', 'value': '192.168.0.1/24'},  # ipv4+cidr
            {'from': '2001:0db8:85a3::/64', 'to': 'cidr', 'value': '2001:0db8:85a3::/64'},  # ipv6+cidr
            {'from': 'fd00:1234:5678:9abc::/48', 'to': 'cidr', 'value': 'fd00:1234:5678:9abc::/48'},  # ipv6+cidr
            {"from": "256.0.0.1", "to": False},
            {"from": "192.168.1.256", "to": False},
            {"from": "3001:0db8:85a3::gabc", "to": False},
            {"from": "invalid_ip_address", "to": False},
            {"from": "10.256.0.1", "to": False},
            {"from": "fd00:1234::1::2", "to": False},
            {"from": "2001:0db8::1::", "to": False},
            {"from": "2001:::", "to": False},
            {"from": "invalid_ip_address", "to": False},
        ]
        for testcase in test_dictionary:
            result = IPTypeValidator().validate(testcase["from"])
            print(result)
            if testcase["to"]:
                type_dictionary[testcase["to"]].value = testcase["value"]
                self.assertEqual(type_dictionary[testcase["to"]], result)
            else:
                self.assertEqual(result, None)

if __name__ == '__main__':
    unittest.main()
