from typing import Any, Optional, Self

from pydantic import BaseModel

from mmisp.worker.jobs.taxonomy.import_taxonomies_config import import_taxonomies_config


class CreateTaxonomiesImportData(BaseModel):
    github_repository_name: str = import_taxonomies_config.taxonomies_repository_name
    github_repository_branch: str = import_taxonomies_config.taxonomies_repository_branch


class ImportTaxonomiesResult(BaseModel):
    success: bool
    imported_taxonomies: Optional[list[str]] = None
    failed_taxonomies: Optional[list[str]] = None
    error_message: Optional[str] = None

    def dict(self: Self, *args, **kwargs) -> dict[str, Any]:
        kwargs["exclude_none"] = True
        return BaseModel.dict(self, *args, **kwargs)
