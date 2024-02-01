import re
import unittest

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import IPTypeValidator
from mmisp.worker.jobs.processfreetext.job_data import ProcessFreeTextData
from mmisp.worker.jobs.processfreetext.processfreetext_job import processfreetext_job, test_split_sentence, \
    test_refang_input


class BasicTestcase(unittest.TestCase):
    def test_validate_ip(self):
        string_to_test: str = "word wprd2 word.23.4.5.6 1.2.3.4 1.2.3.4.5. 1.2.3.4. 55.1.7.8 55.1.2.3.4: 1.2.3.4:70"
        already_split: list = test_split_sentence(string_to_test)
        for words in already_split:
            print(words, ": ", IPTypeValidator().validate(words))
