from typing import Any, Optional, Self

from pydantic import BaseModel

from mmisp.worker.jobs.galaxy.import_galaxies_config import import_galaxies_config


class CreateGalaxiesImportData(BaseModel):
    """Data model for creating galaxies import jobs.

    Attributes:
        github_repository_name: The name of the GitHub repository containing galaxies.
        github_repository_branch: The branch of the GitHub repository to use.
    """

    github_repository_name: str = import_galaxies_config.galaxies_repository_name
    github_repository_branch: str = import_galaxies_config.galaxies_repository_branch


class ImportGalaxiesResult(BaseModel):
    """Data model representing the result of a galaxies import job.

    Attributes:
        success: Indicates whether the import operation was successful.
        imported_galaxies: List of galaxies that were successfully imported.
        failed_galaxies: List of galaxies that failed to import.
        error_message: Error message if the import operation failed.
    """

    success: bool
    imported_galaxies: Optional[list[str]] = None
    failed_galaxies: Optional[list[str]] = None
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
