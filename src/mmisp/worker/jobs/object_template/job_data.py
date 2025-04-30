from typing import Any, Self

from pydantic import BaseModel

from mmisp.worker.jobs.object_template.import_object_templates_config import import_object_templates_config


class CreateObjectTemplatesImportData(BaseModel):
    """Data model for creating object templates import jobs.

    Attributes:
        github_repository_name: The name of the GitHub repository containing object templates.
        github_repository_branch: The branch of the GitHub repository to use.
    """

    github_repository_name: str = import_object_templates_config.object_templates_repository_name
    github_repository_branch: str = import_object_templates_config.object_templates_repository_branch


class ImportObjectTemplatesResult(BaseModel):
    """Data model representing the result of an object templates import job.

    Attributes:
        success: Indicates whether the import operation was successful.
        imported_object_templates: List of object templates that were successfully imported.
        failed_object_templates: List of object templates that failed to import.
        error_message: Error message if the import operation failed.
    """

    success: bool
    imported_object_templates: list[str] | None = None
    failed_object_templates: list[str] | None = None
    error_message: str | None = None

    def dict(self: Self, *args, **kwargs) -> dict[str, Any]:
        """Returns a dictionary representation of the model, excluding None values.

        Args:
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            dict[str, Any]: Dictionary representation of the model.
        """
        kwargs["exclude_none"] = True
        return BaseModel.dict(self, *args, **kwargs)
