import importlib.util
import inspect
import os
import sys
from importlib.machinery import ModuleSpec
from unittest.mock import Mock, call, patch

import pytest
from plugins.enrichment_plugins import dummy_plugin

from mmisp.worker.exceptions.plugin_exceptions import PluginImportError, PluginRegistrationError
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import EnrichmentPluginFactory
from mmisp.worker.plugins.loader import PluginInterface, PluginLoader
from tests.plugins.enrichment_plugins import package_plugin

_plugin_factory: EnrichmentPluginFactory = EnrichmentPluginFactory()


def test_import_missing_plugin():
    with pytest.raises(FileNotFoundError):
        PluginLoader._import_module("/path/to/non/existing/plugin.py")


def test_import_faulty_plugin_module():
    spec: ModuleSpec = importlib.util.find_spec("tests.plugins.enrichment_plugins.non_importable_plugin")
    faulty_plugin_path: str = str(spec.origin)
    with pytest.raises(PluginImportError):
        PluginLoader._import_module(faulty_plugin_path)


def test_import_plugin():
    dummy_plugin_path: str = str(dummy_plugin.__file__)
    PluginLoader.load_plugins([dummy_plugin_path], _plugin_factory)

    # Check if the plugin has been loaded.
    if os.name == "nt":
        assert any(dummy_plugin_path.replace("\\", "\\\\") in str(module) for module in sys.modules.values())
    else:
        assert any(dummy_plugin_path in str(module) for module in sys.modules.values())


def test_import_plugin_package():
    package_plugin_path: str = str(package_plugin.__file__)
    loaded_plugin: PluginInterface = PluginLoader._import_module(package_plugin_path)
    assert loaded_plugin.register == package_plugin.register


def test_load_plugin():
    dummy_plugin_path: str = str(dummy_plugin.__file__)
    PluginLoader.load_plugins([dummy_plugin_path], _plugin_factory)

    # Check if the plugin has been registered in the factory.
    registered: bool = False
    for plugin_module in _plugin_factory._plugins.values():
        if dummy_plugin_path in str(inspect.getmodule(plugin_module).__file__):
            registered = True
            break

    assert registered


def test_load_faulty_plugins():
    non_existing_plugin_path: str = "/path/to/non/existing/plugin.py"
    non_importable_plugin_path: str = "/path/to/non_importable/plugin.py"
    non_registrable_plugin_path: str = "/path/to/non_registrable/plugin.py"

    plugins = [
        non_existing_plugin_path,
        non_importable_plugin_path,
        non_registrable_plugin_path,
    ]

    non_registrable_plugin_mock: Mock = Mock(spec=PluginInterface)
    non_registrable_plugin_mock.register.side_effect = PluginRegistrationError("")

    with patch.object(PluginLoader, "_import_module") as import_module_mock:

        def import_module_function(path: str):
            if path == non_existing_plugin_path:
                raise FileNotFoundError("")
            elif path == non_importable_plugin_path:
                raise PluginImportError("")

            return non_registrable_plugin_mock

        import_module_mock.side_effect = import_module_function

        try:
            PluginLoader.load_plugins(plugins, _plugin_factory)
        except (FileNotFoundError, PluginImportError, PluginRegistrationError):
            assert False, "Loading faulty plugins has triggered an exception."

        import_module_mock.assert_has_calls([call(plugin) for plugin in plugins], any_order=True)


def test_load_invalid_plugins_from_directory():
    with pytest.raises(ValueError):
        PluginLoader.load_plugins_from_directory("/path/to/non/existing/directory", _plugin_factory)
    with pytest.raises(ValueError):
        PluginLoader.load_plugins_from_directory("", _plugin_factory)


def test_load_plugins_from_directory():
    p = "tests/plugins/pluginloader/directory_loader_test"

    PluginLoader.load_plugins_from_directory(p, _plugin_factory)
    plugin_class_names = list(c.__name__ for c in _plugin_factory._plugins.values())

    assert "PluginA" in plugin_class_names
    assert "PluginB" in plugin_class_names


def test_load_package_plugin_from_directory():
    package_plugin_path: str = os.path.dirname(package_plugin.__file__)
    plugin_dir: str = os.path.dirname(package_plugin_path)
    with patch.object(PluginLoader, "load_plugins") as load_plugins_mock:
        PluginLoader.load_plugins_from_directory(plugin_dir, _plugin_factory)
        loaded_plugins: list[str] = load_plugins_mock.call_args[0][0]
        assert package_plugin_path in loaded_plugins
