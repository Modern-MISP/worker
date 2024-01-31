from pydantic import Field
from typing_extensions import Annotated

MispId = Annotated[int, Field(ge=0, lt=10 ** 10)]
#TODO durch int ersetzen?
