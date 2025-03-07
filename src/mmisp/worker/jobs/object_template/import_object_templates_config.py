import logging
import os
from typing import Self

from pydantic import ValidationError

from mmisp.worker.config import ENV_PREFIX, ConfigData

# Environment variable keys for object templates repository configuration.
ENV_OBJECT_TEMPLATES_REPOSITORY_NAME = f"{ENV_PREFIX}_OBJECT_TEMPLATES_REPOSITORY_NAME"
ENV_OBJECT_TEMPLATES_REPOSITORY_BRANCH = f"{ENV_PREFIX}_OBJECT_TEMPLATES_REPOSITORY_BRANCH"

_log = logging.getLogger(__name__)


class ImportObjectTemplatesConfig(ConfigData):
    """Configuration class for importing object templates.

    Attributes:
        object_templates_repository_name: The name of the GitHub repository containing object templates.
        object_templates_repository_branch: The branch of the GitHub repository to use.
    """

    object_templates_repository_name: str = "MISP/misp-objects"
    object_templates_repository_branch: str = "main"

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
            "object_templates_repository_name": ENV_OBJECT_TEMPLATES_REPOSITORY_NAME,
            "object_templates_repository_branch": ENV_OBJECT_TEMPLATES_REPOSITORY_BRANCH,
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
import_object_templates_config: ImportObjectTemplatesConfig = ImportObjectTemplatesConfig()
