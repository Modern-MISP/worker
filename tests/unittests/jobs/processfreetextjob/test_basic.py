import re
import unittest

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import IPTypeValidator
from mmisp.worker.jobs.processfreetext.job_data import ProcessFreeTextData
from mmisp.worker.jobs.processfreetext.processfreetext_job import processfreetext_job, test_split_sentence, \
    test_refang_input


class BasicTestcase(unittest.TestCase):

    def test_split_string_2(self):
        string_to_test: str = "der Angreifer hatte die IP 1.2.3.4. Vielleicht auch die IP 1.2.3.4:80 hat von uns 500 Millionen Euro über Phishing mit Malware prüfsumme 34973274ccef6ab4dfaaf86599792fa9c3fe4689 erbeutet"
        expected_list: list[str] = ['der', 'Angreifer', 'hatte', 'die', 'IP', '1.2.3.4', 'Vielleicht', 'auch', 'die', 'IP', '1.2.3.4:80', 'hat', 'von', 'uns', '500', 'Millionen', 'Euro', 'über', 'Phishing', 'mit', 'Malware', 'prüfsumme', '34973274ccef6ab4dfaaf86599792fa9c3fe4689', 'erbeutet']
        already_split: list = test_split_sentence(string_to_test)
        self.assertEqual(already_split, expected_list)

    def test_split_string_for_ips(self):
        string_to_test: str = "word wprd2 word.23.4.5.6 1.2.3.4 1.2.3.4.5. 1.2.3.4. 55.1.7.8 55.1.2.3.4:"
        expected_list: list[str] = ['word', 'wprd2', 'word.23.4.5.6', '1.2.3.4', '1.2.3.4.5', '1.2.3.4', '55.1.7.8', '55.1.2.3.4:']
        already_split: list = test_split_sentence(string_to_test)
        self.assertEqual(already_split, expected_list)

    def test_validate_ip_basic(self):
        string_to_test: str = "word wprd2 word.23.4.5.6 1.2.3.4 1.2.3.4.5. 1.2.3.4. 55.1.7.8 55.1.2.3.4: 1.2.3.4:70 2001:db8:3333:4444:5555:6666:7777:8888 2001:db8:3333:4444:5555:6666:7777:8888:8001"
        already_split: list = test_split_sentence(string_to_test)
        for words in already_split:
            print(words, ": ", IPTypeValidator().validate(words))

    def test_validate_ip(self):
        string_to_test: str = "word wprd2 word.23.4.5.6 1.2.3.4 1.2.3.4.5. 1.2.3.4. 55.1.7.8 55.1.2.3.4: 1.2.3.4:70"
        already_split: list = test_split_sentence(string_to_test)
        for words in already_split:
            print(words, ": ", IPTypeValidator().validate(words))

    def test_validate_hashes(self):
        pass

    def test_refang_input(self,):
        strings_to_test = [
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
        for string_to_test in strings_to_test:
            string_test = test_refang_input(string_to_test["from"])
            print(string_test)
            self.assertEqual(string_test, string_to_test["to"])


if __name__ == '__main__':
    unittest.main()

