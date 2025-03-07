import logging
import os
from typing import Self

from pydantic import ValidationError

from mmisp.worker.config import ENV_PREFIX, ConfigData

# Environment variable keys for taxonomies repository configuration.
ENV_TAXONOMIES_REPOSITORY_NAME = f"{ENV_PREFIX}_TAXONOMIES_REPOSITORY_NAME"
ENV_TAXONOMIES_REPOSITORY_BRANCH = f"{ENV_PREFIX}_TAXONOMIES_REPOSITORY_BRANCH"

_log = logging.getLogger(__name__)


class ImportTaxonomiesConfig(ConfigData):
    """Configuration class for importing taxonomies.

    Attributes:
        taxonomies_repository_name: The name of the GitHub repository containing taxonomies.
        taxonomies_repository_branch: The branch of the GitHub repository to use.
    """

    taxonomies_repository_name: str = "MISP/misp-taxonomies"
    taxonomies_repository_branch: str = "main"

    def __init__(self: Self) -> None:
        """Initializes the configuration and reads values from environment variables."""
        super().__init__()
        self.read_from_env()

    def read_from_env(self: Self) -> None:
        """Reads configuration values from environment variables.

        If environment variables are set, they override the default values.
        Logs an error if a value cannot be set due to validation issues.
        """
        env_dict: dict = {
            "taxonomies_repository_name": ENV_TAXONOMIES_REPOSITORY_NAME,
            "taxonomies_repository_branch": ENV_TAXONOMIES_REPOSITORY_BRANCH,
        }

        for env in env_dict:
            value: str | None = os.environ.get(env_dict[env])
            if value:
                try:
                    setattr(self, env, value)
                except ValidationError as validation_error:
                    _log.exception(
                        f"{env_dict[env]}: Could not set value from environment variable. {validation_error}"
                    )


# Instantiate the configuration to be used within the application.
import_taxonomies_config: ImportTaxonomiesConfig = ImportTaxonomiesConfig()
