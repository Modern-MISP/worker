from pydantic import BaseModel


class NewTag(BaseModel):
    name: str
    colour: str
    exportable: bool
    orgId: int
    userId: str
    hideTag: bool
    numericalValue: int
    isGalaxy: bool
    isCustomGalaxy: bool
    inherited: int


class Tag(NewTag):
    id: int
