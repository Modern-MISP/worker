from pydantic import BaseModel


class Organisation(BaseModel):
    id: int
    uuid: str
    name: str
