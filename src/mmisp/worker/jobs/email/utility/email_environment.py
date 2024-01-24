from typing import Self

from jinja2 import Environment, PackageLoader, select_autoescape


class EmailEnvironment(Environment):

    __instance: Self = None

    @classmethod
    def get_instance(cls) -> Self:
        if cls.__instance is None:
            EmailEnvironment.__instance = EmailEnvironment()
        return cls.__instance

    def __init__(self):
        if EmailEnvironment.__instance is not None:
            raise RuntimeError("EmailEnvironment is a singleton!")

        EmailEnvironment.__instance = super().__init__(loader=PackageLoader("src"), autoescape=select_autoescape())