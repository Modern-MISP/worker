import logging
import os
from typing import Any, Self

from pydantic import BaseModel, PositiveInt

from mmisp.worker.api.requests_schemas import JobEnum

ENV_PREFIX: str = "MMISP"
"Prefix for the configuration environment variables."


ENV_API_PORT = f"{ENV_PREFIX}_API_PORT"
ENV_API_KEY = f"{ENV_PREFIX}_API_KEY"
ENV_API_HOST = f"{ENV_PREFIX}_API_HOST"
ENV_AUTOSTART_CORRELATION_WORKER = f"{ENV_PREFIX}_AUTOSTART_CORRELATION_WORKER"
ENV_AUTOSTART_EMAIL_WORKER = f"{ENV_PREFIX}_AUTOSTART_EMAIL_WORKER"
ENV_AUTOSTART_ENRICHMENT_WORKER = f"{ENV_PREFIX}_AUTOSTART_ENRICHMENT_WORKER"
ENV_AUTOSTART_EXCEPTION_WORKER = f"{ENV_PREFIX}_AUTOSTART_EXCEPTION_WORKER"
ENV_AUTOSTART_PROCESSFREETEXT_WORKER = f"{ENV_PREFIX}_AUTOSTART_PROCESSFREETEXT_WORKER"
ENV_AUTOSTART_PULL_WORKER = f"{ENV_PREFIX}_AUTOSTART_PULL_JOB"
ENV_AUTOSTART_PUSH_WORKER = f"{ENV_PREFIX}_AUTOSTART_PUSH_JOB"
ENV_WORKER_TERMINATION_TIMEOUT = f"{ENV_PREFIX}_WORKER_TERMINATION_TIMEOUT"

_log = logging.getLogger(__name__)


class ConfigData(BaseModel):
    """
    Base class for configuration data.
    """

    pass


class SystemConfigData(ConfigData):
    """
    Encapsulates the general configuration of the MMISP Worker application.
    """

    api_port: PositiveInt = 5000
    """The port exposing the API."""

    api_key: str = ""
    """The key for the API."""

    api_host: str = "0.0.0.0"
    """The host the API binds to."""

    autostart_correlation_worker: bool = False
    """If True, the correlation worker will be started automatically at application start."""
    autostart_email_worker: bool = False
    """If True, the email worker will be started automatically at application start."""
    autostart_enrichment_worker: bool = False
    """If True, the enrichment worker will be started automatically at application start."""
    autostart_processfreetext_worker: bool = False
    """If True, the process free text worker will be started automatically at application start."""
    autostart_pull_worker: bool = False
    """If True, the pull worker will be started automatically at application start."""
    autostart_push_worker: bool = False
    """If True, the push worker will be started automatically at application start."""
    worker_termination_timeout: int = 30
    """The time in seconds to wait for the worker to terminate before kill."""

    def is_autostart_for_worker_enabled(self: Self, worker: JobEnum) -> Any:
        """
        Returns the autostart configuration for the specified worker.
        :param worker: The worker to check the autostart configuration for.
        """

        worker_config_map: dict[JobEnum, str] = {
            JobEnum.PULL: "autostart_pull_worker",
            JobEnum.PUSH: "autostart_push_worker",
            JobEnum.CORRELATE: "autostart_correlation_worker",
            JobEnum.ENRICHMENT: "autostart_enrichment_worker",
            JobEnum.SEND_EMAIL: "autostart_email_worker",
            JobEnum.PROCESS_FREE_TEXT: "autostart_processfreetext_worker",
        }

        return getattr(self, worker_config_map[worker])


def read_from_env() -> dict:
    """
    Reads the configuration from the environment.
    """

    env_dict: dict[
        str,
        str,
    ] = {
        "api_port": ENV_API_PORT,
        "api_key": ENV_API_KEY,
        "api_host": ENV_API_HOST,
        "autostart_correlation_worker": ENV_AUTOSTART_CORRELATION_WORKER,
        "autostart_email_worker": ENV_AUTOSTART_EMAIL_WORKER,
        "autostart_enrichment_worker": ENV_AUTOSTART_ENRICHMENT_WORKER,
        "autostart_exception_worker": ENV_AUTOSTART_EXCEPTION_WORKER,
        "autostart_processfreetext_worker": ENV_AUTOSTART_PROCESSFREETEXT_WORKER,
        "autostart_pull_worker": ENV_AUTOSTART_PULL_WORKER,
        "autostart_push_worker": ENV_AUTOSTART_PUSH_WORKER,
        "worker_termination_timeout": ENV_WORKER_TERMINATION_TIMEOUT,
    }
    return {
        key: value for key, env_variable in env_dict.items() if (value := os.getenv(env_variable, None)) is not None
    }


system_config_data = SystemConfigData(**read_from_env())
