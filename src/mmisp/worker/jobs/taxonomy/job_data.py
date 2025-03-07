from typing import Any, Optional, Self

from pydantic import BaseModel

from mmisp.worker.jobs.taxonomy.import_taxonomies_config import import_taxonomies_config


class CreateTaxonomiesImportData(BaseModel):
    """Data model for creating taxonomies import jobs.

    Attributes:
        github_repository_name: The name of the GitHub repository containing taxonomies.
        github_repository_branch: The branch of the GitHub repository to use.
    """

    github_repository_name: str = import_taxonomies_config.taxonomies_repository_name
    github_repository_branch: str = import_taxonomies_config.taxonomies_repository_branch


class ImportTaxonomiesResult(BaseModel):
    """Data model representing the result of a taxonomies import job.

    Attributes:
        success: Indicates whether the import operation was successful.
        imported_taxonomies: List of taxonomies that were successfully imported.
        failed_taxonomies: List of taxonomies that failed to import.
        error_message: Error message if the import operation failed.
    """

    success: bool
    imported_taxonomies: Optional[list[str]] = None
    failed_taxonomies: Optional[list[str]] = None
    error_message: Optional[str] = None

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
