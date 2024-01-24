"""
Encapsulates input data classes for the job router.
"""

from pydantic import BaseModel

"""
Data classe for user_id
"""


class UserData(BaseModel):
    user_id: int
