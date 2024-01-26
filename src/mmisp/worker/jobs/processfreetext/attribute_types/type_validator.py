import re
from abc import ABC, abstractmethod

from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.attribute_type import AttributeType
import ipaddress


class TypeValidator(ABC):
    @abstractmethod
    def get_type(self) -> AttributeType:
        pass

    @abstractmethod
    def validate(self, input: str) -> bool:
        pass


class IPTypeValidator(TypeValidator):
    def get_type(self) -> AttributeType:
        return AttributeType(types=['ip-dst', 'ip-src', 'ip-src/ip-dst'], default_type='ip-dst', value=None)

    def validate(self, input: str) -> bool:
        try:
            test = ipaddress.ip_address(input)
            return True
        except ValueError:
            return False


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

    def __init__(self):
        self.__type: AttributeType = None

    def get_type(self) -> AttributeType:
        if self.__type is None:
            raise Exception
        result: AttributeType = self.__type
        self.__type = None
        return result

    def validate(self, input: str) -> bool:
        if "|" in input:
            split_string = input.split("|")
            if len(split_string) == 2:
                if self.__resolve_filename(split_string[0]):
                    found_hash: HashTypeValidator.HashTypes = self.__resolve_hash(split_string[1])
                    if found_hash is not None:
                        self.__type = AttributeType(types=found_hash.composite, default_type=found_hash.composite[0],
                                                    value=input)
                        return True
                    if self.__resolve_ssdeep(split_string[1]):
                        self.__type = AttributeType(types=['fi**lename|ssdeep'], default_type='filename|ssdeep',
                                                    value=input)
                        return True

        found_hash: HashTypeValidator.HashTypes = self.__resolve_hash(input)
        if found_hash is not None:
            self.__type = AttributeType(types=found_hash.single, default_type=found_hash.composite[0],
                                        value=input)
            if BTCTypeValidator().validate(input):
                self.__type.types = self.__type.types.append('btc')
                return True
        if self.__resolve_ssdeep(input):
            self.__type = AttributeType(types='ssdeep', default_type='ssdeep', value=input)
            return True
        return False

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
    def get_type(self) -> AttributeType:
        pass

    def validate(self, input: str) -> bool:
        pass


class DomainFilenameTypeValidator(TypeValidator):
    def get_type(self) -> AttributeType:
        pass

    def validate(self, input: str) -> bool:
        pass


class SimpleRegexTypeValidator(TypeValidator):
    def get_type(self) -> AttributeType:
        pass

    def validate(self, input: str) -> bool:
        pass


class ASTypeValidator(TypeValidator):
    def get_type(self) -> AttributeType:
        pass

    def validate(self, input: str) -> bool:
        pass


class BTCTypeValidator(TypeValidator):
    def get_type(self) -> AttributeType:
        pass

    def validate(self, input: str) -> bool:
        pass
