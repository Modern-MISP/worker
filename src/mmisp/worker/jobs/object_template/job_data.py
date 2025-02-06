from typing import Any, Optional, Self

from pydantic import BaseModel

from mmisp.worker.jobs.object_template.import_object_templates_config import import_object_templates_config


class CreateObjectTemplatesImportData(BaseModel):
    github_repository_name: str = import_object_templates_config.object_templates_repository_name
    github_repository_branch: str = import_object_templates_config.object_templates_repository_branch


class ImportObjectTemplatesResult(BaseModel):
    success: bool
    imported_object_templates: Optional[list[str]] = None
    failed_object_templates: Optional[list[str]] = None
    error_message: Optional[str] = None

    def dict(self: Self, *args, **kwargs) -> dict[str, Any]:
        kwargs["exclude_none"] = True
        return BaseModel.dict(self, *args, **kwargs)
