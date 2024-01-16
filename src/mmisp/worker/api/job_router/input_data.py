"""
Input data classes for the job router.
"""
from enum import Enum

from pydantic import BaseModel


class UserData(BaseModel):
    user_id: int
