import unittest
import re

from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import IPTypeValidator
from mmisp.worker.jobs.processfreetext.attribute_types.attribute_type import AttributeType


class IPTestcase(unittest.TestCase):
    def test_validate_ipv4(self):
        testcases = ["192.168.1.1", "10.0.0.1", "172.16.0.1"]
        attribute_type = AttributeType(types=["ip-dst", "ip-src", "ip-src/ip-dst"], default_type="ip-dst", value="")
        for testcase in testcases:
            result = IPTypeValidator().validate(testcase)
            attribute_type.value = testcase
            self.assertEqual(result, attribute_type)

    def test_validate_ipv6(self):
        testcases = [
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            "fe80::1%eth0",
            "2a00:1450:4007:816::200e",
            "fd3e:4f5a:eee4:ffff::1",
        ]
        attribute_type = AttributeType(types=["ip-dst", "ip-src", "ip-src/ip-dst"], default_type="ip-dst", value="")
        for testcase in testcases:
            result = IPTypeValidator().validate(testcase)
            attribute_type.value = testcase
            self.assertEqual(result, attribute_type)

    def test_validate_ipv4_port(self):
        testcases = ["192.168.1.1:8080", "10.0.0.1:5000"]
        attribute_type = AttributeType(
            types=["ip-dst|port", "ip-src|port", "ip-src|port/ip-dst|port"], default_type="ip-dst|port", value=""
        )
        for testcase in testcases:
            result = IPTypeValidator().validate(testcase)
            attribute_type.value = re.sub(r":", "|", testcase)
            self.assertEqual(result, attribute_type)

    def test_validate_ipv6_port(self):
        testcases = [
            "[2607:f8b0:4005:080a:0000:0000:0000:200e]:8080",
            "[fd12:3456:789a:1bcd:0000:0000:0000:ef02]:12345",
        ]
        attribute_type = AttributeType(
            types=["ip-dst|port", "ip-src|port", "ip-src|port/ip-dst|port"], default_type="ip-dst|port", value=""
        )
        for testcase in testcases:
            result = IPTypeValidator().validate(testcase)
            attribute_type.value = re.sub(r"\[", "", re.sub(r"\]:", "|", testcase))
            self.assertEqual(result, attribute_type)

    def test_validate_ipv4_cidr(self):
        testcases = ["192.168.0.1/24"]
        attribute_type = AttributeType(types=["ip-dst", "ip-src", "ip-src/ip-dst"], default_type="ip-dst", value="")
        for testcase in testcases:
            result = IPTypeValidator().validate(testcase)
            attribute_type.value = testcase
            self.assertEqual(result, attribute_type)

    def test_validate_ipv6_cidr(self):
        testcases = ["2001:0db8:85a3::/64", "fd00:1234:5678:9abc::/48"]
        attribute_type = AttributeType(types=["ip-dst", "ip-src", "ip-src/ip-dst"], default_type="ip-dst", value="")
        for testcase in testcases:
            result = IPTypeValidator().validate(testcase)
            attribute_type.value = testcase
            self.assertEqual(result, attribute_type)


if __name__ == "__main__":
    unittest.main()
