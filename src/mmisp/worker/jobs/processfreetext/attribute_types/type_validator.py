import re
from abc import ABC, abstractmethod
import ipaddress

from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.attribute_type import AttributeType

"""
TODO add to doc that get type was removed and validate has AttributeType
"""


class TypeValidator(ABC):
    @abstractmethod
    def validate(self, input: str) -> bool:
        pass


class IPTypeValidator(TypeValidator):
    def validate(self, input: str) -> AttributeType:
        try:
            test = ipaddress.ip_address(input)
            return AttributeType(types=['ip-dst', 'ip-src', 'ip-src/ip-dst'], default_type='ip-dst', value=input)
        except ValueError:
            return None


class HashTypeValidator(TypeValidator):
    class HashTypes(BaseModel):
        single: list[str]
        composite: list[str]

    hex_hash_types = {
        32: HashTypes(single=['md5', 'imphash', 'x509-fingerprint-md5', 'ja3-fingerprint-md5'],
                      composite=['filename|md5', 'filename|imphash']),
        40: HashTypes(single=['sha1', 'pehash', 'x509-fingerprint-sha1', 'cdhash'],
                      composite=['filename|sha1', 'filename|pehash']),
        56: HashTypes(single=['sha224', 'sha512/224'], composite=['filename|sha224', 'filename|sha512/224']),
        64: HashTypes(single=['sha256', 'authentihash', 'sha512/256', 'x509-fingerprint-sha256'],
                      composite=['filename|sha256', 'filename|authentihash', 'filename|sha512/256']),
        96: HashTypes(single=['sha384'], composite=['filename|sha384']),
        128: HashTypes(single=['sha512'], composite=['filename|sha512'])
    }

    def validate(self, input: str) -> AttributeType:
        if "|" in input:
            split_string = input.split("|")
            if len(split_string) == 2:
                if self.__resolve_filename(split_string[0]):
                    found_hash: HashTypeValidator.HashTypes = self.__resolve_hash(split_string[1])
                    if found_hash is not None:
                        return AttributeType(types=found_hash.composite, default_type=found_hash.composite[0],
                                             value=input)
                    if self.__resolve_ssdeep(split_string[1]):
                        return AttributeType(types=['fi**lename|ssdeep'], default_type='filename|ssdeep',
                                             value=input)

        found_hash: HashTypeValidator.HashTypes = self.__resolve_hash(input)
        if found_hash is not None:
            type = AttributeType(types=found_hash.single, default_type=found_hash.composite[0],
                                 value=input)
            if BTCTypeValidator().validate(input):
                type.types = type.types.append('btc')  # TODO necesary?
            return type
        if self.__resolve_ssdeep(input):
            return AttributeType(types='ssdeep', default_type='ssdeep', value=input)
        return None

    @classmethod
    def __resolve_hash(cls, input: str) -> HashTypes:
        if len(input) in cls.hex_hash_types:
            try:
                int(input, 16)
                return cls.hex_hash_types[len(input)]
            except ValueError:
                return None
        return None

    @classmethod
    def __resolve_ssdeep(cls, input: str) -> bool:
        if re.match('#^[0-9]+:[0-9a-zA-Z/+]+:[0-9a-zA-Z/+]+$#', input):
            if not re.match('#^[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}$#', input):
                return True
        return False

    @classmethod
    def __resolve_filename(cls, input_str: str) -> bool:
        if re.match('/^.:/', input_str) and re.match('.', input_str):
            split = input_str.split('.')
            if not split[-1].isnumeric() and split[-1].isalnum():
                return True
        return False


class EmailTypeValidator(TypeValidator):
    def validate(self, input: str) -> AttributeType:
        try:
            validate_email(input)
            return AttributeType(types=['email', 'email-src', 'email-dst', 'target-email', 'whois-registrant-email'],
                                 default_type='email-src', value=input)
        except EmailNotValidError:
            return None


"""
TODO implement
"""


class DomainFilenameTypeValidator(TypeValidator):
    def validate(self, input: str) -> AttributeType:
        pass


class SimpleRegexTypeValidator(TypeValidator):
    def validate(self, input: str) -> AttributeType:
        if re.match(r"#^cve-[0-9]{4}-[0-9]{4,9}$#i", input):
            return AttributeType(types=['vulnerability'], default_type='vulnerability',
                                 value=input.upper())  # 'CVE' must be uppercase
        if input.startswith('+') or (input.find('-') != -1):
            if (not re.match(r'#^[0-9]{4}-[0-9]{2}-[0-9]{2}$#i', input)):
                if re.match(r"#^(\+)?([0-9]{1,3}(\(0\))?)?[0-9\/\-]{5,}[0-9]$#i", input):
                    return AttributeType(types=['phone-number', 'prtn', 'whois-registrant-phone'],
                                         default_type='phone-number', value=input)
        return None


class ASTypeValidator(TypeValidator):
    def validate(self, input: str) -> AttributeType:
        if re.match(r'#^as[0-9]+$#i', input):
            return AttributeType(types=['AS'], default_type='AS', value=input.upper())
        return None


class BTCTypeValidator(TypeValidator):
    def validate(self, input: str) -> AttributeType:
        if re.match(r"#^([13][a-km-zA-HJ-NP-Z1-9]{25,34})|(bc|tb)1([023456789acdefghjklmnpqrstuvwxyz]{11,71})$#i",
                    input):
            return AttributeType(types=['btc'], default_type='btc', value=input)
        pass
