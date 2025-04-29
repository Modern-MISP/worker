from pydantic import Field
from pydantic_settings import BaseSettings

# Environment variable keys for taxonomies repository configuration.
ENV_TAXONOMIES_REPOSITORY_NAME = "TAXONOMIES_REPOSITORY_NAME"
ENV_TAXONOMIES_REPOSITORY_BRANCH = "TAXONOMIES_REPOSITORY_BRANCH"


class ImportTaxonomiesConfig(BaseSettings):
    """Configuration class for importing taxonomies.

    Attributes:
        taxonomies_repository_name: The name of the GitHub repository containing taxonomies.
        taxonomies_repository_branch: The branch of the GitHub repository to use.
    """

    taxonomies_repository_name: str = Field("MISP/misp-taxonomies", validation_alias=ENV_TAXONOMIES_REPOSITORY_NAME)
    taxonomies_repository_branch: str = Field("main", validation_alias=ENV_TAXONOMIES_REPOSITORY_BRANCH)


# Instantiate the configuration to be used within the application.
import_taxonomies_config: ImportTaxonomiesConfig = ImportTaxonomiesConfig()
