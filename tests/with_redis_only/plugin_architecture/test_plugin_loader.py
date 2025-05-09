import importlib.util
import os
import sys
from importlib.machinery import ModuleSpec

import pytest
from plugins.enrichment_plugins import dummy_plugin

from mmisp.plugins import factory, loader
from mmisp.plugins.exceptions import PluginImportError


def test_import_missing_plugin():
    with pytest.raises(FileNotFoundError):
        loader._import_module("/path/to/non/existing/plugin.py")


def test_import_faulty_plugin_module():
    spec: ModuleSpec = importlib.util.find_spec("tests.plugins.enrichment_plugins.non_importable_plugin")
    faulty_plugin_path: str = str(spec.origin)
    with pytest.raises(PluginImportError):
        loader._import_module(faulty_plugin_path)


def test_import_plugin():
    dummy_plugin_path: str = str(dummy_plugin.__file__)
    loader.load_plugins([dummy_plugin_path])

    # Check if the plugin has been loaded.
    if os.name == "nt":
        assert any(dummy_plugin_path.replace("\\", "\\\\") in str(module) for module in sys.modules.values())
    else:
        assert any(dummy_plugin_path in str(module) for module in sys.modules.values())

    # def test_import_plugin_package():
    #    package_plugin_path: str = str(package_plugin.__file__)
    #    loaded_plugin = loader._import_module(package_plugin_path)
    #    assert loaded_plugin.register == package_plugin.register


def test_load_plugin():
    p = "tests/plugins/pluginloader/module_loader_test/plugin_c.py"
    sys_modules_before = sys.modules.copy().items()
    loader.load_plugins([p])
    sys_modules_after = sys.modules.copy().items()
    diff = list(set(sys_modules_after) - set(sys_modules_before))
    assert len(diff) == 1
    assert diff[0][0].endswith("plugin_c")


def test_load_invalid_plugins_from_directory():
    with pytest.raises(ValueError):
        loader.load_plugins_from_directory("/path/to/non/existing/directory")
    with pytest.raises(ValueError):
        loader.load_plugins_from_directory("")


def test_load_plugins_from_directory():
    p = "tests/plugins/pluginloader/directory_loader_test"

    loader.load_plugins_from_directory(p)
    plugin_class_names = list(c.NAME for c in factory._plugins["enrichment"].values())

    assert "Plugin A" in plugin_class_names
    assert "Plugin B" in plugin_class_names
