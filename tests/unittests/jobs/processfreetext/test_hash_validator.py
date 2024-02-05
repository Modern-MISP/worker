import hashlib
import unittest
import random
import string

from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import HashTypeValidator
from mmisp.worker.jobs.processfreetext.processfreetext_job import _split_text
from mmisp.worker.misp_dataclasses.attribute_type import AttributeType


def get_random_string(length):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))


class HashTestcase(unittest.TestCase):

    def test_split_string_for_hashes(self):
        string_to_test: str = ("word word2 file.txt|abcdef123456 image.jpg|sha256hash invalid.file|invalidhash "
                               "invalidfile.txt|invalidhash validfile.txt|invalidhash file.txt invalid/file.txt "
                               "image.jpg file.123 123:ABCabc/123+abc:XYZxyz/456+xyz 12:34:56 invalid_ssdeep "
                               "abcdef123456 sha256hash invalidhash abc")
        expected_list: list[str] = ['word', 'word2', 'file.txt|abcdef123456', 'image.jpg|sha256hash',
                                    'invalid.file|invalidhash', 'invalidfile.txt|invalidhash',
                                    'validfile.txt|invalidhash', 'file.txt', 'invalid/file.txt', 'image.jpg',
                                    'file.123', '123:ABCabc/123+abc:XYZxyz/456+xyz', '12:34:56', 'invalid_ssdeep',
                                    'abcdef123456', 'sha256hash', 'invalidhash', 'abc']

        already_split: list = _split_text(string_to_test)
        self.assertEqual(already_split, expected_list)

    def test_validate_md5_hash(self):
        testcases = ["5d41402abc4b2a76b9719d911017c592",
                     "7d793037a0760186574b0282f2f435e7",
                     "25d55ad283aa400af464c76d713c07ad",
                     "6713196c32cf55a75d6791b881573f67",
                     "eccbc87e4b5ce2fe28308fd9f2a7baf3"]
        attribute_type: AttributeType = AttributeType(types=HashTypeValidator.hex_hash_types[32].single,
                                                      default_type=
                                                      HashTypeValidator.hex_hash_types[32].single[0],
                                                      value="")
        for testcase in testcases:
            result = HashTypeValidator()._resolve_hash(testcase)
            self.assertEqual(result, HashTypeValidator.hex_hash_types[32])
            result = HashTypeValidator().validate(testcase)
            attribute_type.value = testcase
            self.assertEqual(result, attribute_type)

    def test_validate_sha1_hash(self):
        testcases = ["2ef7bde608ce5404e97d5f042f95f89f1c232871",
                     "6f594f1932be3e3cc02b5a7d5c333d671e9a4f1d",
                     "271c91dc4b0fe1ce54176f07bc029c8b68854fc6"]
        attribute_type: AttributeType = AttributeType(types=HashTypeValidator.hex_hash_types[40].single,
                                                      default_type=
                                                      HashTypeValidator.hex_hash_types[40].single[0],
                                                      value="")
        for testcase in testcases:
            result = HashTypeValidator()._resolve_hash(testcase)
            self.assertEqual(result, HashTypeValidator.hex_hash_types[40])
            result = HashTypeValidator().validate(testcase)
            attribute_type.value = testcase
            self.assertEqual(result, attribute_type)

    def test_validate_sha224_hash(self):
        testcases = ["a5d8a06bccd1c763f8e8f3081cf354b06050c89e46a2c4c97a21de7c",
                     "e7d4878fd75cb9eb7b2e77aa7db8f811007b1c75c7791b4f29b64b3a",
                     "c0c3e1f591f37284da784986f6d79656e388d9f5d5367b0bb773739d"]
        attribute_type: AttributeType = AttributeType(types=HashTypeValidator.hex_hash_types[56].single,
                                                      default_type=HashTypeValidator.hex_hash_types[56].single[0],
                                                      value="")
        for testcase in testcases:
            result = HashTypeValidator()._resolve_hash(testcase)
            self.assertEqual(result, HashTypeValidator.hex_hash_types[56])
            result = HashTypeValidator().validate(testcase)
            attribute_type.value = testcase
            self.assertEqual(result, attribute_type)

    def test_validate_sha256_hash(self):
        testcases = ["a69c5d1f84205a46570bf12c7bf554d978c1d73f4cb2a08b3b8c7f5097dbb0bd",
                     "e0d29e7a51d75c7b23a3ed84a3a6c7a91b31e1139c57ed3511d2684508f6892a",
                     "c6b2f91678e24964b32e6bdf2e0c8a78ba8f4f76c6f51a1d1b61b60c06df32cd"]
        attribute_type: AttributeType = AttributeType(types=HashTypeValidator.hex_hash_types[64].single,
                                                      default_type=HashTypeValidator.hex_hash_types[64].single[0],
                                                      value="")
        for testcase in testcases:
            result = HashTypeValidator()._resolve_hash(testcase)
            self.assertEqual(result, HashTypeValidator.hex_hash_types[64])
            result = HashTypeValidator().validate(testcase)
            attribute_type.value = testcase
            self.assertEqual(result, attribute_type)

    def test_validate_sha384_hash(self):
        testcases = ["a582d7efc849450c78934d3a89a12b546d7e83eb7a4c336b3d8f4a4807ec2b0ba89e76d20b9206f9926922bb99773a57",
                     "9bc17d0b66a418f6780d58545033f9944f4e759256d20e70b18b99a43ce67b19141d13c653c52b079c9f88a4efc0389a",
                     "ca0c8fb10e8b1509cb579e46a51e15a1efbd437a869ee29d2df5c3a710cd552e7745257ec349a9f4bd40f5fe6757426d"]
        attribute_type: AttributeType = AttributeType(types=HashTypeValidator.hex_hash_types[96].single,
                                                      default_type=HashTypeValidator.hex_hash_types[96].single[0],
                                                      value="")

        for testcase in testcases:
            result = HashTypeValidator()._resolve_hash(testcase)
            self.assertEqual(result, HashTypeValidator.hex_hash_types[96])
            result = HashTypeValidator().validate(testcase)
            attribute_type.value = testcase
            self.assertEqual(result, attribute_type)

    def test_validate_sha512_hash(self):
        testcases = [
            "3e340f4d94f63919a222a535946ce53f30bc9fdd39fc145c22a64364c82bbf7ce8e2d8c9b67824e93be2a877eaf759cfc1569a48097af7c3eafe740e95a68f68",
            "e87fc03c8f9b038f51aa6749ff0ea1f155032f6e80d8438a427ac2d4ba773328fc322d2eaaec58e05ad0dd87011f04fb9e0a0c7e276e7082b3d651618b90c51b",
            "b10b29bf89919116e796f09780cf0750039ff14958e1593bf1a08c7ab83338c78b0562b6bcdf1047bdf5f9d18a156c448ba35cf38e9ef833bc0ff8ad6718f371"]
        attribute_type: AttributeType = AttributeType(types=HashTypeValidator.hex_hash_types[128].single,
                                                      default_type=HashTypeValidator.hex_hash_types[128].single[0],
                                                      value="")
        for testcase in testcases:
            result = HashTypeValidator()._resolve_hash(testcase)
            self.assertEqual(result, HashTypeValidator.hex_hash_types[128])
            result = HashTypeValidator().validate(testcase)
            attribute_type.value = testcase
            self.assertEqual(result, attribute_type)

    def test_validate_invalid_hash(self):
        testcases = ["invalid32charstringABCDEF123456",
                     "invalid40charstringABCDEF1234567890abcdef1234",
                     "invalid56charstringABCDEF1234567890abcdef1234567890abcdef1234",
                     "invalid64charstringABCDEF1234567890abcdef1234567890abcdef1234567890abcd",
                     "invalid96charstringABCDEF1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcd",
                     "invalid128charstringABCDEF1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcd"]
        for testcase in testcases:
            result = HashTypeValidator()._resolve_hash(testcase)
            self.assertIsNone(result)
            result = HashTypeValidator().validate(testcase)
            self.assertIsNone(result)

    def test_validate_ssdeep(self):
        testcases = ['24:Ol9rFBzwjx5ZKvBF+bi8RuM4Pp6rG5Yg+q8wIXhMC:qrFBzKx5s8sM4grq8wIXht',
                     '48:9RVyHU/bLrzKkAvcvnU6zjzzNszIpbyzrd:9TyU/bvzK0nUWjzzNszIpm',
                     '96:XVgub8YVvnQXcK+Tqq66aKx7vlqH5Zm03s8BL83ZsVlRJ+:Xuub83HKR6OxIjm03s8m32l/+',
                     '3:z5XJl3rLmXJl3rL:mxQJl3rLm',
                     '3:4eBnsi0L7dC6LFwZdtwQrVzlq6tFqLVR6nJkfS4b37o6xrW0JJH8hJB3T:bnsW7dCeLcFVdtwQrVzJtFqLzV5JH8hJ',
                     '3:5G16/G16/G16:G16/G16/G1',
                     '3:INvZlO6f6JgzElsM1k8q3GG7yXMFOBl6fJrW3xBixK1JgJeLNe9mCNEJ9e9mCNp:E6fJgBlsMeLXk8q3GG7yXMj6fJrW3x',
                     '3:jVvZjVvZjVvZjVvZjVvZjVvZjVvZjVvZjVvZjVvZjVvZj:VvZjVvZjVvZjVvZjVvZjVvZjVvZjVvZjVvZjVvZjVvZjVvZjV']
        for testcase in testcases:
            result = HashTypeValidator()._resolve_ssdeep(testcase)
            self.assertTrue(result)

    def test_validate_ssdeep_hash(self):
        pass

    def test_validate_composite_hashes(self):
        test_dictionary = [
            {'from': '', 'to': None},
            {'from': 'word', 'to': None},
            {'from': 'word|', 'to': None},
            {'from': 'word|word', 'to': None},
            {'from': 'file.txt|invalidhash', 'to': None},
            {'from': 'file|5d41402abc4b2a76b9719d911017c592', 'to': None},
            {'from': 'file.|5d41402abc4b2a76b9719d911017c592', 'to': None},
            {'from': 'file.txt:5d41402abc4b2a76b9719d911017c592', 'to': None},
            {'from': 'file.txt|5d41402abc4b2a76b9719d911017c592|5d41402abc4b2a76b9719d911017c592', 'to': None},
            {'from': 'file.txt|file.txt|5d41402abc4b2a76b9719d911017c592', 'to': None},
            {'from': 'file.txt|5d41402abc4b2a76b9719d911017c592', 'to': 32},
            {'from': 'file.txt|2ef7bde608ce5404e97d5f042f95f89f1c232871', 'to': 40},
            {'from': 'file.txt|e7d4878fd75cb9eb7b2e77aa7db8f811007b1c75c7791b4f29b64b3a', 'to': 56},
            {'from': 'file.txt|e0d29e7a51d75c7b23a3ed84a3a6c7a91b31e1139c57ed3511d2684508f6892a', 'to': 64},
            {
                'from': 'file.txt|ca0c8fb10e8b1509cb579e46a51e15a1efbd437a869ee29d2df5c3a710cd552e7745257ec349a9f4bd40f5fe6757426d',
                'to': 96},
            {
                'from': 'file.txt|b10b29bf89919116e796f09780cf0750039ff14958e1593bf1a08c7ab83338c78b0562b6bcdf1047bdf5f9d18a156c448ba35cf38e9ef833bc0ff8ad6718f371',
                'to': 128},
            {'from': '123:ABCabc/123+abc:XYZxyz/456+xyz',
             'to': AttributeType(types=['ssdeep'], default_type='ssdeep', value='123:ABCabc/123+abc:XYZxyz/456+xyz')}
        ]
        for testcase in test_dictionary:
            result = HashTypeValidator().validate(testcase["from"])
            try:
                self.assertEqual(result, AttributeType(types=HashTypeValidator.hex_hash_types[testcase["to"]].composite,
                                                       default_type=
                                                       HashTypeValidator.hex_hash_types[testcase["to"]].composite[0],
                                                       value=testcase["from"]))
            except (KeyError, TypeError):
                self.assertEqual(result, testcase["to"])

    def test_validate_generated_hashes(self):
        def validate_hash(generated_hash):
            result = HashTypeValidator().validate(generated_hash.hexdigest())
            hash_types: HashTypeValidator.HashTypes = HashTypeValidator.hex_hash_types[
                len(generated_hash.hexdigest())].single
            self.assertEqual(result, AttributeType(types=hash_types, default_type=hash_types[0],
                                                   value=generated_hash.hexdigest()))

        for i in range(15):
            validate_hash(generated_hash=hashlib.md5())
            validate_hash(generated_hash=hashlib.sha1())
            validate_hash(generated_hash=hashlib.sha224())
            validate_hash(generated_hash=hashlib.sha256())
            validate_hash(generated_hash=hashlib.sha384())
            validate_hash(generated_hash=hashlib.sha512())


if __name__ == '__main__':
    unittest.main()
