from pydantic import Field
from pydantic_settings import BaseSettings

# Environment variable keys for object templates repository configuration.
ENV_OBJECT_TEMPLATES_REPOSITORY_NAME = "OBJECT_TEMPLATES_REPOSITORY_NAME"
ENV_OBJECT_TEMPLATES_REPOSITORY_BRANCH = "OBJECT_TEMPLATES_REPOSITORY_BRANCH"


class ImportObjectTemplatesConfig(BaseSettings):
    """Configuration class for importing object templates.

    Attributes:
        object_templates_repository_name: The name of the GitHub repository containing object templates.
        object_templates_repository_branch: The branch of the GitHub repository to use.
    """

    object_templates_repository_name: str = Field(
        "MISP/misp-objects", validation_alias=ENV_OBJECT_TEMPLATES_REPOSITORY_NAME
    )
    object_templates_repository_branch: str = Field("main", validation_alias=ENV_OBJECT_TEMPLATES_REPOSITORY_BRANCH)


# Instantiate the configuration to be used within the application.
import_object_templates_config: ImportObjectTemplatesConfig = ImportObjectTemplatesConfig()
