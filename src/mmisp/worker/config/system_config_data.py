import os
from typing import Any

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

        env_dict: dict = {
            'api_port': ENV_API_PORT,
            'api_key': ENV_API_KEY,
            'api_host': ENV_API_HOST,
        }
        env_bool_dict: dict = {
            'autostart_correlation_worker': ENV_AUTOSTART_CORRELATION_WORKER,
            'autostart_email_worker': ENV_AUTOSTART_EMAIL_WORKER,
            'autostart_enrichment_worker': ENV_AUTOSTART_ENRICHMENT_WORKER,
            'autostart_exception_worker': ENV_AUTOSTART_EXCEPTION_WORKER,
            'autostart_processfreetext_worker': ENV_AUTOSTART_PROCESSFREETEXT_WORKER,
            'autostart_pull_worker': ENV_AUTOSTART_PULL_WORKER,
            'autostart_push_worker': ENV_AUTOSTART_PUSH_WORKER
        }

        def update_value(attribute: str, attribute_value: Any):
            """
            Updates the value of the specified attribute.

            :param attribute: The attribute to update.
            :type attribute: str
            :param attribute_value: The new value for the attribute.
            :type attribute_value: Any
            """
            try:
                setattr(self, attribute, attribute_value)
            except ValidationError as validation_error:
                # TODO: Log ENV Error
                pass

        for env in env_dict:
            value: str = os.environ.get(env_dict[env])
            if value:
                update_value(env, value)

        for env in env_bool_dict:
            value: str = os.environ.get(env_bool_dict[env])
            if value:
                update_value(env, value.lower() == 'true')

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
