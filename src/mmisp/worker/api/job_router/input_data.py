"""
Encapsulates input data classes for the jobs router.
"""

from pydantic import BaseModel


class UserData(BaseModel):
    """
    Data classe for user_id
    """

    user_id: int
    """The id of the user"""
