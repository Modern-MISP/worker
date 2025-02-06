import logging
import os
from typing import Self

from pydantic import ValidationError

from mmisp.worker.config import ENV_PREFIX, ConfigData

ENV_TAXONOMIES_REPOSITORY_NAME = f"{ENV_PREFIX}_TAXONOMIES_REPOSITORY_NAME"
ENV_TAXONOMIES_REPOSITORY_BRANCH = f"{ENV_PREFIX}_TAXONOMIES_REPOSITORY_BRANCH"

_log = logging.getLogger(__name__)


class ImportTaxonomiesConfig(ConfigData):
    taxonomies_repository_name: str = "MISP/misp-taxonomies"
    taxonomies_repository_branch: str = "main"

    def __init__(self: Self) -> None:
        super().__init__()
        self.read_from_env()

    def read_from_env(self: Self) -> None:
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


# Instantiate the configuration to be used within the application
import_taxonomies_config: ImportTaxonomiesConfig = ImportTaxonomiesConfig()
