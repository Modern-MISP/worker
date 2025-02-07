from typing import Any, Optional, Self

from pydantic import BaseModel

from mmisp.worker.jobs.galaxy.import_galaxies_config import import_galaxies_config


class CreateGalaxiesImportData(BaseModel):
    github_repository_name: str = import_galaxies_config.galaxies_repository_name
    github_repository_branch: str = import_galaxies_config.galaxies_repository_branch


class ImportGalaxiesResult(BaseModel):
    success: bool
    imported_galaxies: Optional[list[str]] = None
    failed_galaxies: Optional[list[str]] = None
    error_message: Optional[str] = None

    def dict(self: Self, *args, **kwargs) -> dict[str, Any]:
        kwargs["exclude_none"] = True
        return BaseModel.dict(self, *args, **kwargs)
