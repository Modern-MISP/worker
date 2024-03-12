import unittest

from mmisp.worker.jobs.correlation.correlation_config_data import CorrelationConfigData


class TestConfigData(unittest.TestCase):

    def test_config_data(self):
        config_data: CorrelationConfigData = CorrelationConfigData()
        config_data.read_config_from_env()
        self.assertNotEqual("", config_data.plugin_directory)
        print(config_data.plugin_directory)
