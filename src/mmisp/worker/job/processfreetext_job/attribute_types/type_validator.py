from abc import ABC, abstractmethod
from mmisp.worker.misp_dataclasses.attribute_type import AttributeType


class TypeValidator(ABC):
    @abstractmethod
    def get_type(self) -> AttributeType:
        pass

    @abstractmethod
    def validate(self, input: str) -> bool:
        pass


class IPTypeValidator(TypeValidator):
    def get_type(self) -> AttributeType:
        pass

    def validate(self, input: str) -> bool:
        pass


class HashTypeValidator(TypeValidator):
    def get_type(self) -> AttributeType:
        pass

    def validate(self, input: str) -> bool:
        pass


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
