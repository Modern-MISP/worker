import logging
import os

from pydantic import PositiveInt, ValidationError

from mmisp.worker.api.worker_router.input_data import WorkerEnum
from mmisp.worker.config.config_data import ConfigData, ENV_PREFIX

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

_log = logging.getLogger(__name__)


class SystemConfigData(ConfigData):
    """
    Encapsulates the general configuration of the MMISP Worker application.
    """

    api_port: PositiveInt = 5000
    """The port exposing the API."""

    api_key: str = ""
    """The key for the API."""

    api_host: str = "127.0.0.1"
    """The host the API binds to."""

    autostart_correlation_worker: bool = False
    """If True, the correlation worker will be started automatically at application start."""
    autostart_email_worker: bool = False
    """If True, the email worker will be started automatically at application start."""
    autostart_enrichment_worker: bool = False
    """If True, the enrichment worker will be started automatically at application start."""
    autostart_exception_worker: bool = False
    """If True, the exception worker will be started automatically at application start."""
    autostart_processfreetext_worker: bool = False
    """If True, the process free text worker will be started automatically at application start."""
    autostart_pull_worker: bool = False
    """If True, the pull worker will be started automatically at application start."""
    autostart_push_worker: bool = False
    """If True, the push worker will be started automatically at application start."""

    def __init__(self):
        super().__init__()
        self.read_from_env()

    def read_from_env(self):
        """
        Reads the configuration from the environment.
        """

        env_dict: dict[str, tuple[str, type]] = {
            'api_port': (ENV_API_PORT, int),
            'api_key': (ENV_API_KEY, str),
            'api_host': (ENV_API_HOST, str),
            'autostart_correlation_worker': (ENV_AUTOSTART_CORRELATION_WORKER, bool),
            'autostart_email_worker': (ENV_AUTOSTART_EMAIL_WORKER, bool),
            'autostart_enrichment_worker': (ENV_AUTOSTART_ENRICHMENT_WORKER, bool),
            'autostart_exception_worker': (ENV_AUTOSTART_EXCEPTION_WORKER, bool),
            'autostart_processfreetext_worker': (ENV_AUTOSTART_PROCESSFREETEXT_WORKER, bool),
            'autostart_pull_worker': (ENV_AUTOSTART_PULL_WORKER, bool),
            'autostart_push_worker': (ENV_AUTOSTART_PUSH_WORKER, bool)
        }

        for env in env_dict.keys():
            value: str | bool = os.environ.get(env_dict[env][0])

            if value and env_dict[env][1] == bool:
                value = value.lower() == "true"

            if value is not None and value != "":
                try:
                    setattr(self, env, value)
                except ValidationError as validation_error:
                    _log.exception(f"The given value for the environment variable {env_dict[env][0]} is not valid. "
                                   f"{validation_error}")

    def is_autostart_for_worker_enabled(self, worker: WorkerEnum):
        """
        Returns the autostart configuration for the specified worker.
        :param worker: The worker to check the autostart configuration for.
        """

        worker_config_map: dict[WorkerEnum, str] = {
            WorkerEnum.PULL: 'autostart_pull_worker',
            WorkerEnum.PUSH: 'autostart_push_worker',
            WorkerEnum.CORRELATE: 'autostart_correlation_worker',
            WorkerEnum.ENRICHMENT: 'autostart_enrichment_worker',
            WorkerEnum.SEND_EMAIL: 'autostart_email_worker',
            WorkerEnum.PROCESS_FREE_TEXT: 'autostart_processfreetext_worker'
        }

        return getattr(self, worker_config_map[worker])


system_config_data = SystemConfigData()
