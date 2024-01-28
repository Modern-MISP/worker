import re
from abc import ABC, abstractmethod
import ipaddress
from validators import url

from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.attribute_type import AttributeType

"""
TODO add to doc that get type was removed and validate has AttributeType
and that input is now input_str
add that resolve filename public exists
split Regex validator to Phone and CVE Validator
"""


def resolve_filename(input_str: str) -> bool:
    """
    This method is used to check if a string is a filename
    """
    if re.match('/^.:/', input_str) and re.match('.', input_str):
        split = input_str.split('.')
        if not split[-1].isnumeric() and split[-1].isalnum():
            return True
    return False


class TypeValidator(ABC):
    """
    Abstract model of a Validator Object, which is used to decide, whether a String is a representation
    of a certain Attribute or not. It returns the Attribute Type when an Attribute is found, and None if not
    """

    @abstractmethod
    def validate(self, input_str: str) -> AttributeType:
        """
        This method is used when a String is validated as an Attribute
        """
        pass


class IPTypeValidator(TypeValidator):
    """
    This Class implements a validationmethod for simple IPv4 and IPv6 adresses, without a port
    """

    def validate(self, input_str: str) -> AttributeType:
        """
        This method is used when a String is validated as an IPAttribute
        """
        if self.__validate_ip(input_str):  # checks if the string is an IPv4 or IPv6 IP without a Port
            return AttributeType(types=['ip-dst', 'ip-src', 'ip-src/ip-dst'], default_type='ip-dst', value=input_str)

        if re.search('(:[0-9]{2,5})', input_str):  # checks if the string has a port at the end
            port = input_str.split(":")[-1]
            ip_without_port = re.sub(r'(?<=:)[^:]+$', "", input_str).removesuffix(":")
            if self.__validate_ip(ip_without_port):
                return AttributeType(types=['ip-dst|port', 'ip-src|port', 'ip-src|port/ip-dst|port'],
                                     default_type='ip-dst|port', value=ip_without_port + '|' + port)
                # TODO removed Comment section from return value
            else:  # check if it is a CIDR Block
                if ip_without_port.find('/'):
                    split_ip: list[str] = ip_without_port.split('/')
                    if len(split_ip) == 2 and self.__validate_ip(split_ip[0]) and split_ip[1].isnumeric():
                        return AttributeType(types=['ip-dst', 'ip-src', 'ip-src/ip-dst'], default_type='ip-dst',
                                             value=ip_without_port)
                pass
        else:
            print("not here" + input_str)

    def __validate_ip(self, input_str: str) -> bool:
        try:
            test = ipaddress.ip_address(input_str)
            return True
        except ValueError:
            return False


class DomainFilenameTypeValidator(TypeValidator):
    """
    This Class implements a validationmethod for Domain- and Filenames
    """

    domain_pattern = re.compile(r'^([-\w]+\.)+[a-zA-Z0-9-]+$', re.IGNORECASE | re.UNICODE)
    link_pattern = re.compile(r'^https://([^/]*)', re.IGNORECASE)

    def __init__(self):
        self.__tlds: list[str] = self.__get_tlds()

    @staticmethod
    def __get_tlds() -> list[str]:
        tlds: list[str] = ['biz', 'cat', 'com', 'edu', 'gov', 'int', 'mil', 'net', 'org', 'pro', 'tel', 'aero', 'arpa',
                           'asia', 'coop', 'info', 'jobs', 'mobi', 'name', 'museum', 'travel', 'onion']
        char1 = char2 = 'a'
        for i in range(26):
            for j in range(26):
                tlds.append(char1 + char2)
                char2 = chr(ord(char2) + 1)
            char1 = chr(ord(char1) + 1)
            char2 = 'a'
        return tlds

    def validate(self, input_str: str) -> AttributeType:
        input_without_port: str = self.__remove_port(input_str)
        if '.' in input_without_port:
            split_input: list[str] = input_without_port.split('.')
            if self.domain_pattern.match(input_without_port):
                if split_input[-1] in self.__tlds:
                    if len(split_input) > 2:
                        return AttributeType(types=['hostname', 'domain', 'url', 'filename'], default_type='hostname',
                                             value=input_without_port)
                    else:
                        return AttributeType(types=['domain', 'filename'], default_type='domain',
                                             value=input_without_port)
            else:
                if len(split_input) > 1 and (url(input_without_port) or url('http://' + input_without_port)):
                    if self.link_pattern.match(input_without_port):
                        return AttributeType(types=['link'], default_type='link', value=input_without_port)
                    if '/' in input_without_port:
                        return AttributeType(types=['url'], default_type='url', value=input_without_port)
                if resolve_filename(input_str):
                    return AttributeType(types=['filename'], default_type='filename', value=input_str)
        if '\\' in input_str:
            split_input: list[str] = input_without_port.split('\\')
            if '.' in split_input[-1] or re.match(r'^.:', split_input[0], re.IGNORECASE):
                if resolve_filename(split_input[-1]):
                    return AttributeType(types=['filename'], default_type='filename', value=input_str)
            elif split_input[0]:
                return AttributeType(types= ['regkey'],default_type= 'regkey',value= input_str)
        return None


    @staticmethod
    def __remove_port(input_str: str) -> str:
        if re.search('(:[0-9]{2,5})', input_str):  # checks if the string has a port at the end
            return re.sub(r'(?<=:)[^:]+$', "", input_str).removesuffix(":")
        return input_str


class HashTypeValidator(TypeValidator):
    """
    This Class implements a validationmethod for md5,sha1,sha224,sha256,sha384 and sha512 hashes
    """

    class HashTypes(BaseModel):
        """
        This class encapsulates a HashTypes-Object, which is used to differentiate between single or composite hashes
        """
        single: list[str]
        composite: list[str]

    """
    The hex_hash_types Variable includes a dictionary that maps the length of hashes to the possible types
    """
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

    def validate(self, input_str: str) -> AttributeType:
        """
        This method is used when a String is validated as an HashAttribute
        """
        if "|" in input_str:
            split_string = input_str.split("|")
            if len(split_string) == 2:
                if resolve_filename(split_string[0]):
                    found_hash: HashTypeValidator.HashTypes = self.__resolve_hash(split_string[1])
                    if found_hash is not None:
                        return AttributeType(types=found_hash.composite, default_type=found_hash.composite[0],
                                             value=input_str)
                    if self.__resolve_ssdeep(split_string[1]):
                        return AttributeType(types=['fi**lename|ssdeep'], default_type='filename|ssdeep', # TODO ask if thats wright
                                             value=input_str)

        found_hash: HashTypeValidator.HashTypes = self.__resolve_hash(input_str)
        if found_hash is not None:
            type = AttributeType(types=found_hash.single, default_type=found_hash.composite[0],
                                 value=input_str)
            if BTCTypeValidator().validate(input_str):
                type.types = type.types.append('btc')  # TODO necesary?
            return type
        if self.__resolve_ssdeep(input_str):
            return AttributeType(types='ssdeep', default_type='ssdeep', value=input_str)
        return None

    @classmethod
    def __resolve_hash(cls, input_str: str) -> HashTypes:
        """
        This fuction validates whether the input is a Hash and returns the possible types
        """
        if len(input_str) in cls.hex_hash_types:
            try:
                int(input_str, 16)
                return cls.hex_hash_types[len(input_str)]
            except ValueError:
                return None
        return None

    @classmethod
    def __resolve_ssdeep(cls, input_str: str) -> bool:
        """
        This method is used to resolve a ssdeep Attribute
        """
        if re.match('#^[0-9]+:[0-9a-zA-Z/+]+:[0-9a-zA-Z/+]+$#', input_str):
            if not re.match('#^[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}$#', input_str):
                return True
        return False


class EmailTypeValidator(TypeValidator):
    """
    This Class implements a validationmethod for email-adresses
    """

    def validate(self, input_str: str) -> AttributeType:
        try:
            validate_email(input_str)
            return AttributeType(types=['email', 'email-src', 'email-dst', 'target-email', 'whois-registrant-email'],
                                 default_type='email-src', value=input_str)
        except EmailNotValidError:
            return None


class CVETypeValidator(TypeValidator):
    """
    This Class implements a validationmethod for vulnerabilites
    """

    def validate(self, input_str: str) -> AttributeType:
        if re.match(r"#^cve-[0-9]{4}-[0-9]{4,9}$#i", input_str): # vaildates a CVE
            return AttributeType(types=['vulnerability'], default_type='vulnerability',
                                 value=input_str.upper())  # 'CVE' must be uppercase
        return None

class PhonenumberTypeValidator(TypeValidator):
    """
    This Class implements a validationmethod for phonenumbers
    """

    def validate(self, input_str: str) -> AttributeType:
        if input_str.startswith('+') or (input_str.find('-') != -1): # validates a Phonenumber
            if (not re.match(r'#^[0-9]{4}-[0-9]{2}-[0-9]{2}$#i', input_str)):
                if re.match(r"#^(\+)?([0-9]{1,3}(\(0\))?)?[0-9\/\-]{5,}[0-9]$#i", input_str):
                    return AttributeType(types=['phone-number', 'prtn', 'whois-registrant-phone'],
                                         default_type='phone-number', value=input_str)
        return None


class ASTypeValidator(TypeValidator):
    """
    This Class implements a validationmethod for AS TODO lookup what that is
    """

    def validate(self, input_str: str) -> AttributeType:
        if re.match(r'#^as[0-9]+$#i', input_str):
            return AttributeType(types=['AS'], default_type='AS', value=input_str.upper())
        return None


class BTCTypeValidator(TypeValidator):
    """
    This Class implements a validationmethod for bitcoin-addresses
    """

    def validate(self, input_str: str) -> AttributeType:
        if re.match(r"#^([13][a-km-zA-HJ-NP-Z1-9]{25,34})|(bc|tb)1([023456789acdefghjklmnpqrstuvwxyz]{11,71})$#i",
                    input_str):
            return AttributeType(types=['btc'], default_type='btc', value=input_str)
        pass

