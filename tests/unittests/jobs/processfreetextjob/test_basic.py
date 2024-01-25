import unittest

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import IPTypeValidator
from mmisp.worker.jobs.processfreetext.job_data import ProcessFreeTextData
from mmisp.worker.jobs.processfreetext.processfreetext_job import processfreetext_job, test_split_sentence


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

    def test_validate_ip(self):
        string_to_test: str = "word wprd2 word.23.4.5.6 1.2.3.4 1.2.3.4.5. 1.2.3.4. 55.1.7.8 55.1.2.3.4: 1.2.3.4:70"
        already_split: list = test_split_sentence(string_to_test)
        for words in already_split:
            print(words, ": ", IPTypeValidator().validate(words))


if __name__ == '__main__':
    unittest.main()

