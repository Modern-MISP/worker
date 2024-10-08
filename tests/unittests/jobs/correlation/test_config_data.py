import os
import unittest
from typing import Self
from unittest.mock import patch

from mmisp.worker.jobs.correlation.correlation_config_data import (
    ENV_CORRELATION_PLUGIN_DIRECTORY,
    CorrelationConfigData,
)


class TestConfigData(unittest.TestCase):
    def test_config_data(self: Self):
        saved_env: str | None = os.environ[ENV_CORRELATION_PLUGIN_DIRECTORY]
        example_plugin_path: str = '/usr/local/lib/mmisp/correlation_plugins'
        os.environ[ENV_CORRELATION_PLUGIN_DIRECTORY] = example_plugin_path

        config_data: CorrelationConfigData = CorrelationConfigData()
        config_data.read_config_from_env()

        os.environ[ENV_CORRELATION_PLUGIN_DIRECTORY] = saved_env
        self.assertEqual(example_plugin_path, config_data.plugin_directory)

    @patch("mmisp.worker.jobs.correlation.correlation_config_data.os")
    def test_false_plugin_directory(self: Self, os_mock):
        os_mock.environ.get.return_value = "false"
        os_mock.path.isdir.return_value = False
        config_data: CorrelationConfigData = CorrelationConfigData()
        config_data.read_config_from_env()
        self.assertEqual("", config_data.plugin_directory)
