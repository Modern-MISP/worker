import ipaddress
import re
from abc import ABC, abstractmethod
from typing import Self, Type

from email_validator import EmailNotValidError, validate_email

# mypy declares the import as an error because the module is not typed (only Any) so errors can occur,
# but the module is used only for one method, so no errors should occur
from publicsuffix2 import PublicSuffixList  # type: ignore
from pydantic import BaseModel
from validators import url

from mmisp.worker.jobs.processfreetext.attribute_types.attribute_type import AttributeType
from mmisp.worker.jobs.processfreetext.processfreetext_config_data import ProcessfreetextConfigData

config = ProcessfreetextConfigData()


def resolve_filename(input_str: str) -> bool:
    """
    This method is used to check if a string is a filename, by checking if it has a file extension(an alphanumeric
    not numeric string) or a drive letter

    :param input_str: the string to check
    :type input_str: str
    :return: returns True when the string is a filename, otherwise False
    :rtype: bool
    """
    if re.match(r"^.:/", input_str) or "." in input_str:  # check if it is a drive letter or includes a dot
        split = input_str.split(".")
        if split and not split[-1].isnumeric() and split[-1].isalnum():
            return True  # when the last part is alphanumeric and not numeric
    return False


class TypeValidator(ABC):
    """
    Abstract model of a Validator Object, which is used to decide, whether a String is a representation
    of a certain Attribute or not. It returns the Attribute Type when an Attribute is found, and None if not
    """

    @abstractmethod
    def validate(self: Self, input_str: str) -> AttributeType | None:
        """
        This method is used when a String is validated as an Attribute

        :param input_str: the string to validate
        :type input_str: str
        :return: returns the AttributeType when an Attribute is found, and None if not
        :rtype: AttributeType | None
        """
        pass


class IPTypeValidator(TypeValidator):
    """
    This Class implements a validationmethod for simple IPv4 and IPv6 adresses, without a port
    """

    brackets_pattern: str = r"\[([^]]+)\]"

    def validate(self: Self, input_str: str) -> AttributeType | None:
        """
        This method is used when a String is validated as an IPAttribute
        if the string is an IP, it returns the AttributeType, otherwise None

        it checks if the string is an IPv4 or IPv6 IP with or without a Port, or a CIDR Block

        :param input_str: input string to validate
        :type input_str: str
        :return: returns the AttributeType when an IP is found, otherwise None
        :rtype: AttributeType | None
        """

        ip_without_port: str = input_str

        if self.__validate_ip(input_str):  # checks if the string is an IPv4 or IPv6 IP without a Port
            return AttributeType(types=["ip-dst", "ip-src", "ip-src/ip-dst"], default_type="ip-dst", value=input_str)

        if re.search(r"(:\d{2,5})", input_str):  # checks if the string has a port at the end
            port: str = input_str.split(":")[-1]
            ip_without_port = re.sub(r"(?<=:)\d+$", "", input_str).removesuffix(":")
            # removes [] from ipv6
            match = re.search(self.brackets_pattern, ip_without_port)
            if match:
                extracted_ipv6 = match.group(1)
                ip_without_port = ip_without_port.replace(match.group(0), extracted_ipv6)

            if self.__validate_ip(ip_without_port):
                return AttributeType(
                    types=["ip-dst|port", "ip-src|port", "ip-src|port/ip-dst|port"],
                    default_type="ip-dst|port",
                    value=ip_without_port + "|" + port,
                )

        if ip_without_port.find("/"):  # check if it is a CIDR Block
            split_ip: list[str] = ip_without_port.split("/")
            if len(split_ip) == 2:
                if self.__validate_ip(split_ip[0]) and split_ip[1].isnumeric():
                    return AttributeType(
                        types=["ip-dst", "ip-src", "ip-src/ip-dst"], default_type="ip-dst", value=ip_without_port
                    )
        return None

    def __validate_ip(self: Self, input_str: str) -> bool:
        """
        This method is used to check if a string is an IPv4 or IPv6 IP
        returns True when an IP is found, otherwise False

        :param input_str: the string to check
        :type input_str: str
        :return: returns True when an IP is found, otherwise False
        :rtype: bool
        """
        try:
            ipaddress.ip_address(input_str)
            return True
        except ValueError:
            return False


class DomainFilenameTypeValidator(TypeValidator):
    """
    This Class implements a validationmethod for Domain- and Filenames
    """

    _securityVendorDomains = config.security_vendors
    _domain_pattern = re.compile(r"^([-\w]+\.)+[A-Z0-9-]+$", re.IGNORECASE | re.UNICODE)
    _link_pattern = re.compile(r"^https://([^/]*)", re.IGNORECASE)

    def validate(self: Self, input_str: str) -> AttributeType | None:
        """
        This method is used when a String is validated as a Domain- or FilenameAttribute
        it checks if the string is a Domain, URL, Link, Filename or a Regkey and returns the AttributeType,
        otherwise None

        :param input_str: the string to validate
        :type input_str: str
        :return: returns the AttributeType when a Domain or Filename is found, otherwise None
        :rtype: AttributeType | None
        """

        input_without_port: str = self._remove_port(input_str)
        if "." in input_without_port:
            split_input: list[str] = input_without_port.split(".")
            if self._domain_pattern.match(input_without_port) and PublicSuffixList().get_public_suffix(
                split_input[-1], strict=True
            ):  # validate TLD
                if len(split_input) > 2:
                    return AttributeType(
                        types=["hostname", "domain", "url", "filename"],
                        default_type="hostname",
                        value=input_without_port,
                    )
                else:
                    return AttributeType(types=["domain", "filename"], default_type="domain", value=input_without_port)
            else:
                if len(split_input) > 1 and (url(input_without_port) or url("http://" + input_without_port)):
                    if self._is_link(input_without_port):
                        return AttributeType(types=["link"], default_type="link", value=input_without_port)
                    if "/" in input_without_port:
                        return AttributeType(types=["url"], default_type="url", value=input_without_port)
                if resolve_filename(input_str):
                    return AttributeType(types=["filename"], default_type="filename", value=input_str)

        if "\\" in input_str:
            split_input = input_without_port.split("\\")
            if split_input[0]:
                return AttributeType(types=["regkey"], default_type="regkey", value=input_str)
        return None

    @staticmethod
    def _remove_port(input_str: str) -> str:
        """
        This method is used to remove the port from a string

        :param input_str: the string to remove the port from
        :type input_str: str
        :return: returns the string without the port
        :rtype: str
        """
        if re.search(r"(:\d{2,5})", input_str):  # checks if the string has a port at the end
            return re.sub(r"(?<=:)[^:]+$", "", input_str).removesuffix(":")
        return input_str

    def _is_link(self: Self, input_str: str) -> bool:
        """
        This method is used to check if a string is a link by checking if the domain is a security vendor domain

        :param input_str: the string to check
        :type input_str: str
        :return: returns True when the string is a link, otherwise False
        :rtype: bool
        """
        found_link = self._link_pattern.match(input_str)

        if found_link:
            domain_to_check = ""
            domain_parts = list(reversed(found_link.group(1).split(".")))  # Extract and reverse the domain parts

            for domain_part in domain_parts:
                domain_to_check = domain_part + domain_to_check
                if domain_to_check in self._securityVendorDomains:
                    return True
                domain_to_check = "." + domain_to_check
        return False


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
        32: HashTypes(
            single=["md5", "imphash", "x509-fingerprint-md5", "ja3-fingerprint-md5"],
            composite=["filename|md5", "filename|imphash"],
        ),
        40: HashTypes(
            single=["sha1", "pehash", "x509-fingerprint-sha1", "cdhash"], composite=["filename|sha1", "filename|pehash"]
        ),
        56: HashTypes(single=["sha224", "sha512/224"], composite=["filename|sha224", "filename|sha512/224"]),
        64: HashTypes(
            single=["sha256", "authentihash", "sha512/256", "x509-fingerprint-sha256"],
            composite=["filename|sha256", "filename|authentihash", "filename|sha512/256"],
        ),
        96: HashTypes(single=["sha384"], composite=["filename|sha384"]),
        128: HashTypes(single=["sha512"], composite=["filename|sha512"]),
    }

    def validate(self: Self, input_str: str) -> AttributeType | None:
        """
        This method is used when a String is validated as an HashAttribute
        it checks if the string is a single or composite hash and returns the AttributeType, otherwise None
        valid hashes are md5,sha1,sha224,sha256,sha384,sha512 and ssdeep

        :param input_str: input string to validate
        :type input_str: str
        :return: returns the AttributeType when a Hash is found, otherwise None
        :rtype: AttributeType | None
        """

        if "|" in input_str:  # checks if the string could be a composite hash
            split_string = input_str.split("|")
            if len(split_string) == 2 and resolve_filename(split_string[0]):  # checks if the first part is a filename
                found_hash: HashTypeValidator.HashTypes | None = self._resolve_hash(split_string[1])  # checks if the
                # second part is a hash
                if found_hash is not None:
                    return AttributeType(
                        types=found_hash.composite, default_type=found_hash.composite[0], value=input_str
                    )
                if self._resolve_ssdeep(split_string[1]):  # checks if the second part is a ssdeep hash
                    return AttributeType(types=["fi**lename|ssdeep"], default_type="filename|ssdeep", value=input_str)

        found_hash = self._resolve_hash(input_str)  # checks if the string is a single hash
        if found_hash is not None:
            hash_type = AttributeType(types=found_hash.single, default_type=found_hash.single[0], value=input_str)
            if BTCTypeValidator().validate(input_str):  # checks if the hash is a btc hash
                hash_type.types.append("btc")
            return hash_type
        if self._resolve_ssdeep(input_str):  # checks if the string is a ssdeep hash
            return AttributeType(types=["ssdeep"], default_type="ssdeep", value=input_str)
        return None

    @classmethod
    def _resolve_hash(cls: Type["HashTypeValidator"], input_str: str) -> HashTypes | None:
        """
        This function validates whether the input is a Hash and returns the possible types
        valid hashes are md5,sha1,sha224,sha256,sha384,sha512

        :param input_str: input string to validate
        :type input_str: str
        :return: returns the possible types of the hash when a hash was found, otherwise None
        :rtype: HashTypes
        """
        if len(input_str) in cls.hex_hash_types:
            try:
                int(input_str, 16)
                return cls.hex_hash_types[len(input_str)]
            except ValueError:
                return None
        return None

    @classmethod
    def _resolve_ssdeep(cls: Type["HashTypeValidator"], input_str: str) -> bool:
        """
        This method is used to resolve a ssdeep Hash

        :param input_str:
        :type input_str:
        :return:
        :rtype:
        """
        if re.match(r"^\d+:[0-9a-zA-Z/+]+:[0-9a-zA-Z/+]+$", input_str):
            if not re.match(r"^\d{1,2}:\d{1,2}:\d{1,2}$", input_str):
                return True
        return False


class EmailTypeValidator(TypeValidator):
    """
    This Class implements a validationmethod for email-adresses
    """

    def validate(self: Self, input_str: str) -> AttributeType | None:
        """
        This method is used when a String is validated as an EmailAttribute

        :param input_str: input string to validate
        :type input_str: str
        :return: returns the AttributeType when an Email address is found, otherwise None
        :rtype: AttributeType | None
        """
        try:
            validate_email(input_str, check_deliverability=False)
            return AttributeType(
                types=["email", "email-src", "email-dst", "target-email", "whois-registrant-email"],
                default_type="email-src",
                value=input_str,
            )
        except EmailNotValidError:
            return None


class CVETypeValidator(TypeValidator):
    """
    This Class implements a validationmethod for vulnerabilites
    """

    cve_regex = re.compile(r"^cve-\d{4}-\d{4,9}$", re.IGNORECASE)

    def validate(self: Self, input_str: str) -> AttributeType | None:
        """
         This method is used when a String is validated as an CVEAttribute

        :param input_str: input string to validate
        :type input_str: str
        :return: returns the AttributeType when a CVE is found, otherwise None
        :rtype: AttributeType | None
        """
        if self.cve_regex.match(input_str):  # vaildates a CVE
            return AttributeType(
                types=["vulnerability"], default_type="vulnerability", value=input_str.upper()
            )  # 'CVE' must be uppercase
        return None


class PhonenumberTypeValidator(TypeValidator):
    """
    This Class implements a validationmethod for phonenumbers
    """

    date_regex = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    phone_number_regex = re.compile(r"^(\+)?(\d{1,3}(\(0\))?)?[0-9/\-]{5,}\d$", re.IGNORECASE)

    def validate(self: Self, input_str: str) -> AttributeType | None:
        """
        This method is used when a String is validated as an PhoneNumberAttribute

        :param input_str: input string to validate
        :type input_str: str
        :return: returns the AttributeType when a PhoneNumber is found, otherwise None
        :rtype: AttributeType | None
        """
        if input_str.startswith("+") or (input_str.find("-") != -1):
            if not self.date_regex.match(input_str):  # checks if the string is not a date
                if self.phone_number_regex.match(input_str):  # checks if the string is a phone number
                    return AttributeType(
                        types=["phone-number", "prtn", "whois-registrant-phone"],
                        default_type="phone-number",
                        value=input_str,
                    )
        return None


class ASTypeValidator(TypeValidator):
    """
    This Class implements a validationmethod for AS Numbers
    """

    as_regex = re.compile(r"^as\d+$", re.IGNORECASE)

    def validate(self: Self, input_str: str) -> AttributeType | None:
        """
        This method is used when a String is validated as an ASAttribute

        :param input_str: input string to validate
        :type input_str: str
        :return: returns the AttributeType when an AS is found, otherwise None
        :rtype: AttributeType | None
        """
        if self.as_regex.match(input_str):
            return AttributeType(types=["AS"], default_type="AS", value=input_str.upper())
        return None


class BTCTypeValidator(TypeValidator):
    """
    This Class implements a validationmethod for bitcoin-addresses
    """

    bitcoin_address_regex = re.compile(
        r"^(?:[13][a-km-zA-HJ-NP-Z1-9]{25,34}|(bc|tb)1[023456789acdefghjklmnpqrstuvwxyz]{11,71})$", re.IGNORECASE
    )

    def validate(self: Self, input_str: str) -> AttributeType | None:
        """
        This method is used when a String is validated as an BTCAttribute

        :param input_str: input string to validate
        :type input_str: str
        :return: returns the AttributeType when a BTC address is found, otherwise None
        :rtype: AttributeType | None
        """
        if self.bitcoin_address_regex.match(input_str):
            return AttributeType(types=["btc"], default_type="btc", value=input_str)
        return None
