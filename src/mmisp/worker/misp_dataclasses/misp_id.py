from pydantic import Field
from typing_extensions import Annotated

MispId = Annotated[int, Field(ge=0, lt=10 ** 10)]
"""
Type definition for a MISP ID.
implements restrictions
"""