from pydantic import BaseModel


class MispServerVersion(BaseModel):
    version: str
    pymisp_recommended_version: str | None = None
    perm_sync: bool
    perm_sighting: bool
    perm_galaxy_editor: bool
    request_encoding: list[str] | None = None
    filter_sightings: bool
