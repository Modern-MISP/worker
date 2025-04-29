import logging

from pydantic import Field
from pydantic_settings import BaseSettings

# Environment variable keys for galaxies repository configuration.
ENV_GALAXIES_REPOSITORY_NAME = "GALAXIES_REPOSITORY_NAME"
ENV_GALAXIES_REPOSITORY_BRANCH = "GALAXIES_REPOSITORY_BRANCH"

_log = logging.getLogger(__name__)


class ImportGalaxiesConfig(BaseSettings):
    """Configuration class for importing galaxies.

    Attributes:
        galaxies_repository_name: The name of the GitHub repository containing galaxies.
        galaxies_repository_branch: The branch of the GitHub repository to use.
    """

    galaxies_repository_name: str = Field("MISP/misp-galaxy", validation_alias=ENV_GALAXIES_REPOSITORY_NAME)
    galaxies_repository_branch: str = Field("main", validation_alias=ENV_GALAXIES_REPOSITORY_BRANCH)


# Instantiate the configuration to be used within the application.
import_galaxies_config: ImportGalaxiesConfig = ImportGalaxiesConfig()
