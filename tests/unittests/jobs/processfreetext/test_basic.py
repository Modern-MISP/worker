import unittest

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import resolve_filename
from mmisp.worker.jobs.processfreetext.job_data import ProcessFreeTextData, ProcessFreeTextResponse
from mmisp.worker.jobs.processfreetext.processfreetext_job import processfreetext_job, _refang_input, \
    _split_text
from mmisp.worker.jobs.processfreetext.attribute_types.attribute_type import AttributeType


class BasicTestcase(unittest.TestCase):

    def test_split_string(self):
        string_to_test: str = ("der Angreifer hatte die IP 1.2.3.4. Vielleicht auch die IP 1.2.3.4:80 hat von uns 500 "
                               "Millionen Euro über Phishing mit Malware prüfsumme "
                               "34973274ccef6ab4dfaaf86599792fa9c3fe4689 erbeutet")
        expected_list: list[str] = ['der', 'Angreifer', 'hatte', 'die', 'IP', '1.2.3.4', 'Vielleicht', 'auch', 'die',
                                    'IP', '1.2.3.4:80', 'hat', 'von', 'uns', '500', 'Millionen', 'Euro', 'über',
                                    'Phishing', 'mit', 'Malware', 'prüfsumme',
                                    '34973274ccef6ab4dfaaf86599792fa9c3fe4689', 'erbeutet']
        already_split: list = _split_text(string_to_test)
        self.assertEqual(already_split, expected_list)

    def test_split_string_for_ips(self):
        string_to_test: str = "word wprd2 word.23.4.5.6 1.2.3.4 1.2.3.4.5. 1.2.3.4. 55.1.7.8 55.1.2.3.4:"
        expected_list: list[str] = ['word', 'wprd2', 'word.23.4.5.6', '1.2.3.4', '1.2.3.4.5', '1.2.3.4', '55.1.7.8',
                                    '55.1.2.3.4:']
        already_split: list = _split_text(string_to_test)
        self.assertEqual(already_split, expected_list)

    def test_resolve_filename(self):
        test_data = [
            {'from': 'example.txt', 'to': True},
            {'from': 'document.pdf', 'to': True},
            {'from': 'image.jpeg', 'to': True},
            {'from': 'code.py', 'to': True},
            {'from': 'data_file_2022.csv', 'to': True},
            {'from': 'README.md', 'to': True},
            {'from': 'file.txt123', 'to': True},
            {'from': 'dir/file.txt', 'to': True},
            {'from': '/path/to/file.txt', 'to': True},
            {'from': 'file_with.dots.txt', 'to': True},
            {'from': 'file.with.multiple.dots.txt', 'to': True},
            {'from': 'no_extension', 'to': False},
            {'from': 'file123', 'to': False},
            {'from': 'invalid/slash/file.txt', 'to': True}
        ]

        for testcase in test_data:
            result = resolve_filename(testcase["from"])
            self.assertEqual(result, testcase["to"])

    def test_refang_input(self):
        test_data = [
            {"from": "test", "to": "test"},
            {"from": "test[i]", "to": "testi"},
            {"from": "[i]test[i]", "to": "itesti"},
            {"from": "test[i][i]", "to": "testii"},
            {"from": "hxxp hxtp htxp meow h[tt]p", "to": "http http http http http"},
            {"from": "[.] [dot] (dot)", "to": ". . ."},
            {"from": "hxxp://", "to": "http://"},
            {"from": "[@] [at]", "to": "@ @"},
            {"from": "[:]", "to": ":"}
        ]
        for string_to_test in test_data:
            string_test = _refang_input(string_to_test["from"])
            self.assertEqual(string_test, string_to_test["to"])

    def test_processfreetext_job(self):
        user = UserData(user_id=1)
        data = ProcessFreeTextData(data="der Angreifer mit der IP 1.2.3.4 hat von uns 500 Millionen Euro über "
                                        "Phishing mit Malware prüfsumme 34973274ccef6ab4dfaaf86599792fa9c3fe4689 "
                                        "erbeutet")
        result = processfreetext_job(user, data)
        result_array: list[AttributeType] = [
            AttributeType(types=['ip-dst', 'ip-src', 'ip-src/ip-dst'], default_type='ip-dst', value='1.2.3.4'),
            AttributeType(types=['sha1', 'pehash', 'x509-fingerprint-sha1', 'cdhash'], default_type='sha1',
                          value='34973274ccef6ab4dfaaf86599792fa9c3fe4689')]

        self.assertEqual(result, ProcessFreeTextResponse(attributes=result_array))

    def test_processfreetext_job2(self):
        user = UserData(user_id=1)
        data = ProcessFreeTextData(
            data="Dieser testfall soll alle Attribute aus dem freien Text extrahieren. Hierin sind zum Beispiel die "
                 "IP 1.2.3.4, die IP 1.4.6.8:8080, die Prüfsumme 34973274ccef6ab4dfaaf86599792fa9c3fe4689 und die "
                 "E-Mail test@gmail.com enthalten.")
        result = processfreetext_job(user, data)
        result_array: list[AttributeType] = [
            AttributeType(types=['ip-dst', 'ip-src', 'ip-src/ip-dst'], default_type='ip-dst', value='1.2.3.4'),
            AttributeType(types=['ip-dst|port', 'ip-src|port', 'ip-src|port/ip-dst|port'], default_type='ip-dst|port',
                          value='1.4.6.8|8080'),
            AttributeType(types=['sha1', 'pehash', 'x509-fingerprint-sha1', 'cdhash'], default_type='sha1',
                          value='34973274ccef6ab4dfaaf86599792fa9c3fe4689'),
            AttributeType(types=['email', 'email-src', 'email-dst', 'target-email', 'whois-registrant-email'],
                          default_type='email-src', value='test@gmail.com')]

        self.assertEqual(result, ProcessFreeTextResponse(attributes=result_array))


if __name__ == '__main__':
    unittest.main()
