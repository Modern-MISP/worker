import hashlib
import re

import pytest

from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.processfreetext.attribute_types.attribute_type import AttributeType
from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import (
    ASTypeValidator,
    BTCTypeValidator,
    CVETypeValidator,
    DomainFilenameTypeValidator,
    EmailTypeValidator,
    HashTypeValidator,
    IPTypeValidator,
    PhonenumberTypeValidator,
    resolve_filename,
)
from mmisp.worker.jobs.processfreetext.job_data import ProcessFreeTextData, ProcessFreeTextResponse
from mmisp.worker.jobs.processfreetext.processfreetext_job import _refang_input, _split_text, processfreetext_job, queue


def test_validate_AS():
    test_dictionary = ["as123", "aS456", "as789", "aS123", "AS456", "AS789"]
    attribute_type = AttributeType(types=["AS"], default_type="AS", value="")
    for testcase in test_dictionary:
        result = ASTypeValidator().validate(testcase)
        attribute_type.value = testcase.upper()
        assert result == attribute_type


def test_validate_AS_invalid():
    test_dictionary = ["vs1234", "aS@4567", "as7890@", "AS|1234", "wAS4567", "AS7890a"]
    for testcase in test_dictionary:
        result = ASTypeValidator().validate(testcase)
        assert result is None


def test_split_string_basic():
    string_to_test: str = "die IP " + "\n" + " 1.2.3.4. 1.2.3.4:80 34973274ccef6ab4dfaaf86599792fa9c3fe4689. "
    expected_list: list[str] = [
        "die",
        "IP",
        "1.2.3.4",
        "1.2.3.4:80",
        "34973274ccef6ab4dfaaf86599792fa9c3fe4689",
    ]
    already_split: list = _split_text(string_to_test)
    assert already_split == expected_list


def test_split_string():
    string_to_test: str = (
        "der Angreifer hatte die IP 1.2.3.4. Vielleicht auch die IP 1.2.3.4:80 hat von uns 500 "
        "Millionen Euro über Phishing mit Malware prüfsumme "
        "34973274ccef6ab4dfaaf86599792fa9c3fe4689 erbeutet"
    )
    expected_list: list[str] = [
        "der",
        "Angreifer",
        "hatte",
        "die",
        "IP",
        "1.2.3.4",
        "Vielleicht",
        "auch",
        "die",
        "IP",
        "1.2.3.4:80",
        "hat",
        "von",
        "uns",
        "500",
        "Millionen",
        "Euro",
        "über",
        "Phishing",
        "mit",
        "Malware",
        "prüfsumme",
        "34973274ccef6ab4dfaaf86599792fa9c3fe4689",
        "erbeutet",
    ]
    already_split: list = _split_text(string_to_test)
    assert already_split == expected_list


def test_split_string_for_ips():
    string_to_test: str = "word wprd2 word.23.4.5.6 1.2.3.4 1.2.3.4.5. 1.2.3.4. 55.1.7.8 55.1.2.3.4:"
    expected_list: list[str] = [
        "word",
        "wprd2",
        "word.23.4.5.6",
        "1.2.3.4",
        "1.2.3.4.5",
        "1.2.3.4",
        "55.1.7.8",
        "55.1.2.3.4:",
    ]
    already_split: list = _split_text(string_to_test)
    assert already_split == expected_list


def test_resolve_filename():
    test_data = [
        {"from": "example.txt", "to": True},
        {"from": "document.pdf", "to": True},
        {"from": "image.jpeg", "to": True},
        {"from": "code.py", "to": True},
        {"from": "data_file_2022.csv", "to": True},
        {"from": "README.md", "to": True},
        {"from": "file.txt123", "to": True},
        {"from": "dir/file.txt", "to": True},
        {"from": "/path/to/file.txt", "to": True},
        {"from": "file_with.dots.txt", "to": True},
        {"from": "file.with.multiple.dots.txt", "to": True},
        {"from": "no_extension", "to": False},
        {"from": "file123", "to": False},
        {"from": "invalid/slash/file.txt", "to": True},
    ]

    for testcase in test_data:
        result = resolve_filename(testcase["from"])
        assert result == testcase["to"]


def test_refang_input():
    test_data = [
        {"from": "test", "to": "test"},
        {"from": "test[i]", "to": "testi"},
        {"from": "[i]test[i]", "to": "itesti"},
        {"from": "test[i][i]", "to": "testii"},
        {"from": "hxxp hxtp htxp meow h[tt]p", "to": "http http http http http"},
        {"from": "[.] [dot] (dot)", "to": ". . ."},
        {"from": "hxxp://", "to": "http://"},
        {"from": "[@] [at]", "to": "@ @"},
        {"from": "[:]", "to": ":"},
    ]
    for string_to_test in test_data:
        string_test = _refang_input(string_to_test["from"])
        assert string_test == string_to_test["to"]


@pytest.mark.asyncio
async def test_processfreetext_job():
    async with queue:
        user = UserData(user_id=1)
        data = ProcessFreeTextData(
            data="der Angreifer mit der IP 1.2.3.4 hat von uns 500 Millionen Euro über "
            "Phishing mit Malware prüfsumme 34973274ccef6ab4dfaaf86599792fa9c3fe4689 "
            "erbeutet"
        )
        result = await processfreetext_job.run(user, data)
        result_array: list[AttributeType] = [
            AttributeType(types=["ip-dst", "ip-src", "ip-src/ip-dst"], default_type="ip-dst", value="1.2.3.4"),
            AttributeType(
                types=["sha1", "pehash", "x509-fingerprint-sha1", "cdhash"],
                default_type="sha1",
                value="34973274ccef6ab4dfaaf86599792fa9c3fe4689",
            ),
        ]

        assert result == ProcessFreeTextResponse(attributes=result_array)


@pytest.mark.asyncio
async def test_processfreetext_job2():
    async with queue:
        user = UserData(user_id=1)
        data = ProcessFreeTextData(
            data="Dieser testfall soll alle Attribute aus dem freien Text extrahieren. Hierin sind zum Beispiel die "
            "IP 1.2.3.4, die IP 1.4.6.8:8080, die Prüfsumme 34973274ccef6ab4dfaaf86599792fa9c3fe4689 und die "
            "E-Mail test@gmail.com enthalten."
        )
        result = await processfreetext_job.run(user, data)
        result_array: list[AttributeType] = [
            AttributeType(types=["ip-dst", "ip-src", "ip-src/ip-dst"], default_type="ip-dst", value="1.2.3.4"),
            AttributeType(
                types=["ip-dst|port", "ip-src|port", "ip-src|port/ip-dst|port"],
                default_type="ip-dst|port",
                value="1.4.6.8|8080",
            ),
            AttributeType(
                types=["sha1", "pehash", "x509-fingerprint-sha1", "cdhash"],
                default_type="sha1",
                value="34973274ccef6ab4dfaaf86599792fa9c3fe4689",
            ),
            AttributeType(
                types=["email", "email-src", "email-dst", "target-email", "whois-registrant-email"],
                default_type="email-src",
                value="test@gmail.com",
            ),
        ]

        assert result == ProcessFreeTextResponse(attributes=result_array)


def test_validate_btc():
    testcases = [
        "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        "1Hb9NFrEfe4DTnCReaDgzmRb6PFTLbFro8",
        "1MGLPkvFCGzpmsWGFBYq5siXUdCQ6gTpkA",
        "1Emo4qE9HKfQQCV5Fqgt12j1C2quZbBy39",
        "1Jq5r2kbPDiwTMukhfJ1tM6S2SCyKWDCGZ",
        "1D7zAVyQ2eL4cqxtFv8n6GwTGyekGkQU5u",
        "1LFjaFStkknC9CUYKjAEDiAL1y1iYXKmAL",
        "1A8xbFfxif9WwX3L1D7nA1FX4x6gKjxdzM",
        "1Fd8RUb9JhYJWefDhAqbXsWwuaE2KZf8PR",
        "1F7JYkso6pG1nKjjL6FstzTKThTbKUS8Vt",
    ]
    for testcase in testcases:
        result = BTCTypeValidator().validate(testcase)
        assert result == AttributeType(types=["btc"], default_type="btc", value=testcase)


def test_validate_btc_invalid():
    testcases = [
        "1Abcdefghijklmnopqrstuvwxyz1234567890",
        "1InvalidAddressAbcdefghijklmnopqrstuv",
        "1NotABitcoinAddress9876543210zyxwvuts",
        "1FakeBitcoinAddressAbcdefghijklmnopq",
        "1Invalid123AddressAbcdefghijklmnopqr",
        "1TestBitcoinAddress@Abcdefghijklmnop",
        "1Fake123BitcoinAddress|Abcdefghijklm",
        "1NotRealBitcoinAddressAbcdefghijklmn",
        "1Invalid987654AddressAbcdefghijklmno",
        "1FakeBitcoin123AddressasdasdAbcdefghijkl",
    ]
    for testcase in testcases:
        result = BTCTypeValidator().validate(testcase)
        assert result is None


def test_validate_CVE():
    testcases = ["cve-2021-1234", "cve-2019-56789", "cVe-2020-9876543", "cve-2018-54321", "CVE-2017-123456789"]
    for testcase in testcases:
        result = CVETypeValidator().validate(testcase)
        assert result == AttributeType(types=["vulnerability"], default_type="vulnerability", value=testcase.upper())


def test_validate_invalid_CVE():
    testcases = ["cve-12345", "CVE-ABCDE", "CVE-2022-12345-67890", "cve-ABCD-5678"]
    for testcase in testcases:
        result = CVETypeValidator().validate(testcase)
        assert result is None


def test_validate_hostname():
    testcases = ["test.example.com", "test.example.com:8000"]
    for testcase in testcases:
        result = DomainFilenameTypeValidator().validate(testcase)
        if ":" in testcase:
            assert result == AttributeType(
                types=["hostname", "domain", "url", "filename"],
                default_type="hostname",
                value=testcase.split(":")[0],
            )
        else:
            assert result == AttributeType(
                types=["hostname", "domain", "url", "filename"], default_type="hostname", value=testcase
            )


def test_validate_domain():
    testcases = ["test.com", "example.com"]
    for testcase in testcases:
        result = DomainFilenameTypeValidator().validate(testcase)
        assert result == AttributeType(types=["domain", "filename"], default_type="domain", value=testcase)


def test_validate_url():
    testcases = [
        "https://www.example.com/test",
        "https://www.example.com/test?param1=value1&param2=value2",
        "ftp://www.example.com",
    ]
    for testcase in testcases:
        result = DomainFilenameTypeValidator().validate(testcase)
        assert result == AttributeType(types=["url"], default_type="url", value=testcase)


def test_validate_filename():
    testcases = ["example.txt", "document.pdf", "image.jpeg", "subdomain!.example.com", "\\example-file.txt"]
    for testcase in testcases:
        result = DomainFilenameTypeValidator().validate(testcase)
        assert result == AttributeType(types=["filename"], default_type="filename", value=testcase)


def test_validate_regkey():
    testcases = [
        r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion",
        r"HKLM\System\InvalidKey",
        r"HKCU\Software\KeyWithoutSpaces",
    ]
    for testcase in testcases:
        result = DomainFilenameTypeValidator().validate(testcase)
        assert result == AttributeType(types=["regkey"], default_type="regkey", value=testcase)


def test_validate_link():
    testcases = ["https://virustotal.com"]
    for testcase in testcases:
        result = DomainFilenameTypeValidator().validate(testcase)
        assert result == AttributeType(types=["link"], default_type="link", value=testcase)


def test_validate_invalid():
    testcases = ["example.123:8000", "my_domain.com!", "invalid-link"]
    for testcase in testcases:
        result = DomainFilenameTypeValidator().validate(testcase)
        assert result is None


def test_validate_is_link():
    assert DomainFilenameTypeValidator()._is_link("https://virustotal.com")


def test_validate_email():
    testcases = [
        "john.doe@gmail.com",
        "alice_smith123@gmail.com",
        "contact@company.org",
        "info+support@website.net",
        "user123@domain-name.co.uk",
    ]
    for testcase in testcases:
        result = EmailTypeValidator().validate(testcase)
        assert result == AttributeType(
            types=["email", "email-src", "email-dst", "target-email", "whois-registrant-email"],
            default_type="email-src",
            value=testcase,
        )


def test_validate_invalid_email():
    testcases = ["john.doe@example", "@gmail.com", "user123@", "invalid-email@.org "]
    for testcase in testcases:
        result = EmailTypeValidator().validate(testcase)
        assert result is None


def test_split_string_for_hashes():
    string_to_test: str = (
        "word word2 file.txt|abcdef123456 image.jpg|sha256hash invalid.file|invalidhash "
        "invalidfile.txt|invalidhash validfile.txt|invalidhash file.txt invalid/file.txt "
        "image.jpg file.123 123:ABCabc/123+abc:XYZxyz/456+xyz 12:34:56 invalid_ssdeep "
        "abcdef123456 sha256hash invalidhash abc"
    )
    expected_list: list[str] = [
        "word",
        "word2",
        "file.txt|abcdef123456",
        "image.jpg|sha256hash",
        "invalid.file|invalidhash",
        "invalidfile.txt|invalidhash",
        "validfile.txt|invalidhash",
        "file.txt",
        "invalid/file.txt",
        "image.jpg",
        "file.123",
        "123:ABCabc/123+abc:XYZxyz/456+xyz",
        "12:34:56",
        "invalid_ssdeep",
        "abcdef123456",
        "sha256hash",
        "invalidhash",
        "abc",
    ]

    already_split: list = _split_text(string_to_test)
    assert already_split == expected_list


def test_validate_md5_hash():
    testcases = [
        "5d41402abc4b2a76b9719d911017c592",
        "7d793037a0760186574b0282f2f435e7",
        "25d55ad283aa400af464c76d713c07ad",
        "6713196c32cf55a75d6791b881573f67",
        "eccbc87e4b5ce2fe28308fd9f2a7baf3",
    ]
    attribute_type: AttributeType = AttributeType(
        types=HashTypeValidator.hex_hash_types[32].single,
        default_type=HashTypeValidator.hex_hash_types[32].single[0],
        value="",
    )
    for testcase in testcases:
        result = HashTypeValidator()._resolve_hash(testcase)
        assert result == HashTypeValidator.hex_hash_types[32]
        result = HashTypeValidator().validate(testcase)
        attribute_type.value = testcase
        assert result == attribute_type


def test_validate_sha1_hash():
    testcases = [
        "2ef7bde608ce5404e97d5f042f95f89f1c232871",
        "6f594f1932be3e3cc02b5a7d5c333d671e9a4f1d",
        "271c91dc4b0fe1ce54176f07bc029c8b68854fc6",
    ]
    attribute_type: AttributeType = AttributeType(
        types=HashTypeValidator.hex_hash_types[40].single,
        default_type=HashTypeValidator.hex_hash_types[40].single[0],
        value="",
    )
    for testcase in testcases:
        result = HashTypeValidator()._resolve_hash(testcase)
        assert result == HashTypeValidator.hex_hash_types[40]
        result = HashTypeValidator().validate(testcase)
        attribute_type.value = testcase
        assert result == attribute_type


def test_validate_sha224_hash():
    testcases = [
        "a5d8a06bccd1c763f8e8f3081cf354b06050c89e46a2c4c97a21de7c",
        "e7d4878fd75cb9eb7b2e77aa7db8f811007b1c75c7791b4f29b64b3a",
        "c0c3e1f591f37284da784986f6d79656e388d9f5d5367b0bb773739d",
    ]
    attribute_type: AttributeType = AttributeType(
        types=HashTypeValidator.hex_hash_types[56].single,
        default_type=HashTypeValidator.hex_hash_types[56].single[0],
        value="",
    )
    for testcase in testcases:
        result = HashTypeValidator()._resolve_hash(testcase)
        assert result == HashTypeValidator.hex_hash_types[56]
        result = HashTypeValidator().validate(testcase)
        attribute_type.value = testcase
        assert result == attribute_type


def test_validate_sha256_hash():
    testcases = [
        "a69c5d1f84205a46570bf12c7bf554d978c1d73f4cb2a08b3b8c7f5097dbb0bd",
        "e0d29e7a51d75c7b23a3ed84a3a6c7a91b31e1139c57ed3511d2684508f6892a",
        "c6b2f91678e24964b32e6bdf2e0c8a78ba8f4f76c6f51a1d1b61b60c06df32cd",
    ]
    attribute_type: AttributeType = AttributeType(
        types=HashTypeValidator.hex_hash_types[64].single,
        default_type=HashTypeValidator.hex_hash_types[64].single[0],
        value="",
    )
    for testcase in testcases:
        result = HashTypeValidator()._resolve_hash(testcase)
        assert result == HashTypeValidator.hex_hash_types[64]
        result = HashTypeValidator().validate(testcase)
        attribute_type.value = testcase
        assert result == attribute_type


def test_validate_sha384_hash():
    testcases = [
        "a582d7efc849450c78934d3a89a12b546d7e83eb7a4c336b3d8f4a4807ec2b0ba89e76d20b9206f9926922bb99773a57",
        "9bc17d0b66a418f6780d58545033f9944f4e759256d20e70b18b99a43ce67b19141d13c653c52b079c9f88a4efc0389a",
        "ca0c8fb10e8b1509cb579e46a51e15a1efbd437a869ee29d2df5c3a710cd552e7745257ec349a9f4bd40f5fe6757426d",
    ]
    attribute_type: AttributeType = AttributeType(
        types=HashTypeValidator.hex_hash_types[96].single,
        default_type=HashTypeValidator.hex_hash_types[96].single[0],
        value="",
    )

    for testcase in testcases:
        result = HashTypeValidator()._resolve_hash(testcase)
        assert result == HashTypeValidator.hex_hash_types[96]
        result = HashTypeValidator().validate(testcase)
        attribute_type.value = testcase
        assert result == attribute_type


def test_validate_sha512_hash():
    testcases = [
        "3e340f4d94f63919a222a535946ce53f30bc9fdd39fc145c22a64364c82bbf7ce8e2d8c9b67824e93be2a877eaf759cfc1569a48097af7c3eafe740e95a68f68",
        "e87fc03c8f9b038f51aa6749ff0ea1f155032f6e80d8438a427ac2d4ba773328fc322d2eaaec58e05ad0dd87011f04fb9e0a0c7e276e7082b3d651618b90c51b",
        "b10b29bf89919116e796f09780cf0750039ff14958e1593bf1a08c7ab83338c78b0562b6bcdf1047bdf5f9d18a156c448ba35cf38e9ef833bc0ff8ad6718f371",
    ]
    attribute_type: AttributeType = AttributeType(
        types=HashTypeValidator.hex_hash_types[128].single,
        default_type=HashTypeValidator.hex_hash_types[128].single[0],
        value="",
    )
    for testcase in testcases:
        result = HashTypeValidator()._resolve_hash(testcase)
        assert result == HashTypeValidator.hex_hash_types[128]
        result = HashTypeValidator().validate(testcase)
        attribute_type.value = testcase
        assert result == attribute_type


def test_validate_invalid_hash():
    testcases = [
        "invalid32charstringABCDEF123456",
        "invalid40charstringABCDEF1234567890abcdef1234",
        "invalid56charstringABCDEF1234567890abcdef1234567890abcdef1234",
        "invalid64charstringABCDEF1234567890abcdef1234567890abcdef1234567890abcd",
        "invalid96charstringABCDEF1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcd",
        "invalid128charstringABCDEF1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcd",
    ]
    for testcase in testcases:
        result = HashTypeValidator()._resolve_hash(testcase)
        assert result is None
        result = HashTypeValidator().validate(testcase)
        assert result is None


def test_validate_ssdeep():
    testcases = [
        "24:Ol9rFBzwjx5ZKvBF+bi8RuM4Pp6rG5Yg+q8wIXhMC:qrFBzKx5s8sM4grq8wIXht",
        "48:9RVyHU/bLrzKkAvcvnU6zjzzNszIpbyzrd:9TyU/bvzK0nUWjzzNszIpm",
        "96:XVgub8YVvnQXcK+Tqq66aKx7vlqH5Zm03s8BL83ZsVlRJ+:Xuub83HKR6OxIjm03s8m32l/+",
        "3:z5XJl3rLmXJl3rL:mxQJl3rLm",
        "3:4eBnsi0L7dC6LFwZdtwQrVzlq6tFqLVR6nJkfS4b37o6xrW0JJH8hJB3T:bnsW7dCeLcFVdtwQrVzJtFqLzV5JH8hJ",
        "3:5G16/G16/G16:G16/G16/G1",
        "3:INvZlO6f6JgzElsM1k8q3GG7yXMFOBl6fJrW3xBixK1JgJeLNe9mCNEJ9e9mCNp:E6fJgBlsMeLXk8q3GG7yXMj6fJrW3x",
        "3:jVvZjVvZjVvZjVvZjVvZjVvZjVvZjVvZjVvZjVvZjVvZj:VvZjVvZjVvZjVvZjVvZjVvZjVvZjVvZjVvZjVvZjVvZjVvZjV",
    ]
    for testcase in testcases:
        result = HashTypeValidator()._resolve_ssdeep(testcase)
        assert result
        result = HashTypeValidator().validate(testcase)
        assert result == AttributeType(types=["ssdeep"], default_type="ssdeep", value=testcase)


def test_validate_invalid_ssdeep():
    testcases = [
        "invalidssdeepstring",
        "ABCDEF123456",
        "23:ABCDEF1234567890abcdef1234",
        "34:ABCDEF1234567890abcdef1234567890abcdef1234",
        "48:ABCDEF1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcd",
    ]
    for testcase in testcases:
        result = HashTypeValidator()._resolve_ssdeep(testcase)
        assert not result
        result = HashTypeValidator().validate(testcase)
        assert result is None


def test_validate_composite_md5_hash():
    testcases = [
        "file.txt|5d41402abc4b2a76b9719d911017c592",
        "file.txt|7d793037a0760186574b0282f2f435e7",
        "file.txt|25d55ad283aa400af464c76d713c07ad",
        "file.txt|6713196c32cf55a75d6791b881573f67",
        "file.txt|eccbc87e4b5ce2fe28308fd9f2a7baf3",
    ]
    attribute_type: AttributeType = AttributeType(
        types=HashTypeValidator.hex_hash_types[32].composite,
        default_type=HashTypeValidator.hex_hash_types[32].composite[0],
        value="",
    )
    for testcase in testcases:
        result = HashTypeValidator().validate(testcase)
        attribute_type.value = testcase
        assert result == attribute_type


def test_validate_composite_sha1_hash():
    testcases = [
        "file.txt|2ef7bde608ce5404e97d5f042f95f89f1c232871",
        "file.txt|6f594f1932be3e3cc02b5a7d5c333d671e9a4f1d",
        "file.txt|271c91dc4b0fe1ce54176f07bc029c8b68854fc6",
    ]
    attribute_type: AttributeType = AttributeType(
        types=HashTypeValidator.hex_hash_types[40].composite,
        default_type=HashTypeValidator.hex_hash_types[40].composite[0],
        value="",
    )
    for testcase in testcases:
        result = HashTypeValidator().validate(testcase)
        attribute_type.value = testcase
        assert result == attribute_type


def test_validate_composite_sha224_hash():
    testcases = [
        "file.txt|a5d8a06bccd1c763f8e8f3081cf354b06050c89e46a2c4c97a21de7c",
        "file.txt|e7d4878fd75cb9eb7b2e77aa7db8f811007b1c75c7791b4f29b64b3a",
        "file.txt|c0c3e1f591f37284da784986f6d79656e388d9f5d5367b0bb773739d",
    ]
    attribute_type: AttributeType = AttributeType(
        types=HashTypeValidator.hex_hash_types[56].composite,
        default_type=HashTypeValidator.hex_hash_types[56].composite[0],
        value="",
    )
    for testcase in testcases:
        result = HashTypeValidator().validate(testcase)
        attribute_type.value = testcase
        assert result == attribute_type


def test_validate_composite_sha256_hash():
    testcases = [
        "file.txt|a69c5d1f84205a46570bf12c7bf554d978c1d73f4cb2a08b3b8c7f5097dbb0bd",
        "file.txt|e0d29e7a51d75c7b23a3ed84a3a6c7a91b31e1139c57ed3511d2684508f6892a",
        "file.txt|c6b2f91678e24964b32e6bdf2e0c8a78ba8f4f76c6f51a1d1b61b60c06df32cd",
    ]
    attribute_type: AttributeType = AttributeType(
        types=HashTypeValidator.hex_hash_types[64].composite,
        default_type=HashTypeValidator.hex_hash_types[64].composite[0],
        value="",
    )
    for testcase in testcases:
        result = HashTypeValidator().validate(testcase)
        attribute_type.value = testcase
        assert result == attribute_type


def test_validate_composite_sha384_hash():
    testcases = [
        "file.txt|a582d7efc849450c78934d3a89a12b546d7e83eb7a4c336b3d8f4a4807ec2b0ba89e76d20b9206f9926922bb99773a57",
        "file.txt|9bc17d0b66a418f6780d58545033f9944f4e759256d20e70b18b99a43ce67b19141d13c653c52b079c9f88a4efc0389a",
        "file.txt|ca0c8fb10e8b1509cb579e46a51e15a1efbd437a869ee29d2df5c3a710cd552e7745257ec349a9f4bd40f5fe6757426d",
    ]
    attribute_type: AttributeType = AttributeType(
        types=HashTypeValidator.hex_hash_types[96].composite,
        default_type=HashTypeValidator.hex_hash_types[96].composite[0],
        value="",
    )
    for testcase in testcases:
        result = HashTypeValidator().validate(testcase)
        attribute_type.value = testcase
        assert result == attribute_type


def test_validate_composite_sha512_hash():
    testcases = [
        "file.txt|3e340f4d94f63919a222a535946ce53f30bc9fdd39fc145c22a64364c82bbf7ce8e2d8c9b67824e93be2a877eaf759cfc1569a48097af7c3eafe740e95a68f68",
        "file.txt|e87fc03c8f9b038f51aa6749ff0ea1f155032f6e80d8438a427ac2d4ba773328fc322d2eaaec58e05ad0dd87011f04fb9e0a0c7e276e7082b3d651618b90c51b",
        "file.txt|b10b29bf89919116e796f09780cf0750039ff14958e1593bf1a08c7ab83338c78b0562b6bcdf1047bdf5f9d18a156c448ba35cf38e9ef833bc0ff8ad6718f371",
    ]
    attribute_type: AttributeType = AttributeType(
        types=HashTypeValidator.hex_hash_types[128].composite,
        default_type=HashTypeValidator.hex_hash_types[128].composite[0],
        value="",
    )
    for testcase in testcases:
        result = HashTypeValidator().validate(testcase)
        attribute_type.value = testcase
        assert result == attribute_type


def test_validate_composite_ssdeep():
    testcases = [
        "file.txt|24:Ol9rFBzwjx5ZKvBF+bi8RuM4Pp6rG5Yg+q8wIXhMC:qrFBzKx5s8sM4grq8wIXht",
        "file.txt|48:9RVyHU/bLrzKkAvcvnU6zjzzNszIpbyzrd:9TyU/bvzK0nUWjzzNszIpm",
        "file.txt|96:XVgub8YVvnQXcK+Tqq66aKx7vlqH5Zm03s8BL83ZsVlRJ+:Xuub83HKR6OxIjm03s8m32l/+",
    ]
    attribute_type: AttributeType = AttributeType(types=["fi**lename|ssdeep"], default_type="filename|ssdeep", value="")
    for testcase in testcases:
        result = HashTypeValidator().validate(testcase)
        attribute_type.value = testcase
        assert result == attribute_type


def test_validate_invalid_composite_hash():
    testcases = [
        "file.txt|invalid32charstringABCDEF123456",
        "file.txt|invalid40charstringABCDEF1234567890abcdef1234",
        "file.txt|invalid56charstringABCDEF1234567890abcdef1234567890abcdef1234",
        "file.txt|invalid64charstringABCDEF1234567890abcdef1234567890abcdef1234567890abcd",
        "file.txt|invalid96charstringABCDEF1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcd",
        "file.txt|invalid128charstringABCDEF1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcd",
    ]
    for testcase in testcases:
        result = HashTypeValidator().validate(testcase)
        assert result is None


def test_validate_hash_btc_resembles():
    testcases = ["1D41412ABC4B2A76B9719D911117c592"]

    for testcase in testcases:
        result = HashTypeValidator().validate(testcase)
        assert result == AttributeType(
            types=["md5", "imphash", "x509-fingerprint-md5", "ja3-fingerprint-md5", "btc"],
            default_type="md5",
            value="1D41412ABC4B2A76B9719D911117c592",
        )


def test_validate_generated_single_hashes():
    def validate_hash(generated_hash):
        result = HashTypeValidator().validate(generated_hash.hexdigest())
        hash_types: HashTypeValidator.HashTypes = HashTypeValidator.hex_hash_types[
            len(generated_hash.hexdigest())
        ].single
        assert result == AttributeType(types=hash_types, default_type=hash_types[0], value=generated_hash.hexdigest())

    for _ in range(15):
        validate_hash(generated_hash=hashlib.md5())
        validate_hash(generated_hash=hashlib.sha1())
        validate_hash(generated_hash=hashlib.sha224())
        validate_hash(generated_hash=hashlib.sha256())
        validate_hash(generated_hash=hashlib.sha384())
        validate_hash(generated_hash=hashlib.sha512())


def test_validate_generated_composite_hashes():
    def validate_hash(generated_hash):
        result = HashTypeValidator().validate(f"file.txt|{generated_hash.hexdigest()}")
        hash_types: HashTypeValidator.HashTypes = HashTypeValidator.hex_hash_types[
            len(generated_hash.hexdigest())
        ].composite
        assert result == AttributeType(
            types=hash_types, default_type=hash_types[0], value=f"file.txt|{generated_hash.hexdigest()}"
        )

    for _ in range(15):
        validate_hash(generated_hash=hashlib.md5())
        validate_hash(generated_hash=hashlib.sha1())
        validate_hash(generated_hash=hashlib.sha224())
        validate_hash(generated_hash=hashlib.sha256())
        validate_hash(generated_hash=hashlib.sha384())
        validate_hash(generated_hash=hashlib.sha512())


def test_validate_ipv4():
    testcases = ["192.168.1.1", "10.0.0.1", "172.16.0.1"]
    attribute_type = AttributeType(types=["ip-dst", "ip-src", "ip-src/ip-dst"], default_type="ip-dst", value="")
    for testcase in testcases:
        result = IPTypeValidator().validate(testcase)
        attribute_type.value = testcase
        assert result == attribute_type


def test_validate_ipv6():
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
        assert result == attribute_type


def test_validate_ipv4_port():
    testcases = ["192.168.1.1:8080", "10.0.0.1:5000"]
    attribute_type = AttributeType(
        types=["ip-dst|port", "ip-src|port", "ip-src|port/ip-dst|port"], default_type="ip-dst|port", value=""
    )
    for testcase in testcases:
        result = IPTypeValidator().validate(testcase)
        attribute_type.value = re.sub(r":", "|", testcase)
        assert result == attribute_type


def test_validate_ipv6_port():
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
        assert result == attribute_type


def test_validate_ipv4_cidr():
    testcases = ["192.168.0.1/24"]
    attribute_type = AttributeType(types=["ip-dst", "ip-src", "ip-src/ip-dst"], default_type="ip-dst", value="")
    for testcase in testcases:
        result = IPTypeValidator().validate(testcase)
        attribute_type.value = testcase
        assert result == attribute_type


def test_validate_ipv6_cidr():
    testcases = ["2001:0db8:85a3::/64", "fd00:1234:5678:9abc::/48"]
    attribute_type = AttributeType(types=["ip-dst", "ip-src", "ip-src/ip-dst"], default_type="ip-dst", value="")
    for testcase in testcases:
        result = IPTypeValidator().validate(testcase)
        attribute_type.value = testcase
        assert result == attribute_type


def test_validate_phone_number():
    testcases = ["+1555-123-4567", "+61298765432", "+81312345678", "+81312345678", "123-456-789"]
    for testcase in testcases:
        result = PhonenumberTypeValidator().validate(testcase)
        assert result == AttributeType(
            types=["phone-number", "prtn", "whois-registrant-phone"],
            default_type="phone-number",
            value=testcase,
        )


def test_validate_phone_number_invalid():
    testcases = ["+1(0)12345", "12345/67890", "12345/67890/12345"]
    for testcase in testcases:
        result = PhonenumberTypeValidator().validate(testcase)
        assert result is None
