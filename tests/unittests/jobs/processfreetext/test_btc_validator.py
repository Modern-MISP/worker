import unittest

from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import BTCTypeValidator
from mmisp.worker.jobs.processfreetext.attribute_types.attribute_type import AttributeType


class BTCTestcase(unittest.TestCase):

    def test_validate_btc(self):
        testcases = [
            '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
            '1Hb9NFrEfe4DTnCReaDgzmRb6PFTLbFro8',
            '1MGLPkvFCGzpmsWGFBYq5siXUdCQ6gTpkA',
            '1Emo4qE9HKfQQCV5Fqgt12j1C2quZbBy39',
            '1Jq5r2kbPDiwTMukhfJ1tM6S2SCyKWDCGZ',
            '1D7zAVyQ2eL4cqxtFv8n6GwTGyekGkQU5u',
            '1LFjaFStkknC9CUYKjAEDiAL1y1iYXKmAL',
            '1A8xbFfxif9WwX3L1D7nA1FX4x6gKjxdzM',
            '1Fd8RUb9JhYJWefDhAqbXsWwuaE2KZf8PR',
            '1F7JYkso6pG1nKjjL6FstzTKThTbKUS8Vt'
        ]
        for testcase in testcases:
            result = BTCTypeValidator().validate(testcase)
            self.assertEqual(result, AttributeType(types=['btc'], default_type='btc', value=testcase))

    def test_validate_btc_invalid(self):
        testcases = [
            '1Abcdefghijklmnopqrstuvwxyz1234567890',
            '1InvalidAddressAbcdefghijklmnopqrstuv',
            '1NotABitcoinAddress9876543210zyxwvuts',
            '1FakeBitcoinAddressAbcdefghijklmnopq',
            '1Invalid123AddressAbcdefghijklmnopqr',
            '1TestBitcoinAddress@Abcdefghijklmnop',
            '1Fake123BitcoinAddress|Abcdefghijklm',
            '1NotRealBitcoinAddressAbcdefghijklmn',
            '1Invalid987654AddressAbcdefghijklmno',
            '1FakeBitcoin123AddressasdasdAbcdefghijkl'
        ]
        for testcase in testcases:
            result = BTCTypeValidator().validate(testcase)
            self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
