import pytest
from plugins.enrichment_plugins import dns_resolver, dummy_plugin
from plugins.enrichment_plugins.dns_resolver import DNSResolverPlugin
from plugins.enrichment_plugins.dummy_plugin import DummyPlugin

from mmisp.worker.exceptions.plugin_exceptions import NotAValidPlugin, PluginNotFound, PluginRegistrationError
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import EnrichmentPluginFactory
from mmisp.worker.plugins.plugin import PluginInfo

_plugin_factory: EnrichmentPluginFactory = EnrichmentPluginFactory()


def test_register():
    _plugin_factory.register(DummyPlugin)
    assert DummyPlugin in _plugin_factory._plugins.values()


def test_register_invalid_plugin():
    class InvalidPlugin:
        pass

    with pytest.raises(NotAValidPlugin):
        _plugin_factory.register(InvalidPlugin)  # type: ignore


def test_register_existing_plugin_name():
    class DummyPluginClone(DummyPlugin):
        pass

    with pytest.raises(PluginRegistrationError):
        _plugin_factory.register(DummyPluginClone)


def test_unregister():
    dummy_plugin_name: str = DummyPlugin.PLUGIN_INFO.NAME
    dummy_plugin.register(_plugin_factory)
    assert _plugin_factory.is_plugin_registered(dummy_plugin_name)

    _plugin_factory.unregister(DummyPlugin.PLUGIN_INFO.NAME)

    assert not _plugin_factory.is_plugin_registered(dummy_plugin_name)

    with pytest.raises(PluginNotFound):
        _plugin_factory.unregister("random_not_existing_plugin_name")


def test_get_plugin_info():
    dummy_plugin_name: str = DummyPlugin.PLUGIN_INFO.NAME
    dummy_plugin.register(_plugin_factory)
    assert DummyPlugin.PLUGIN_INFO == _plugin_factory.get_plugin_info(dummy_plugin_name)

    with pytest.raises(PluginNotFound):
        _plugin_factory.get_plugin_info("random_not_existing_plugin_name")


def test_get_plugins():
    dummy_plugin.register(_plugin_factory)
    dns_resolver.register(_plugin_factory)
    loaded_plugins: list[PluginInfo] = _plugin_factory.get_plugins()
    assert DummyPlugin.PLUGIN_INFO in loaded_plugins
    assert DNSResolverPlugin.PLUGIN_INFO in loaded_plugins


def test_is_plugin_registered():
    dummy_plugin.register(_plugin_factory)
    with pytest.raises(ValueError):
        _plugin_factory.is_plugin_registered("")
    assert not _plugin_factory.is_plugin_registered("random_not_existing_plugin_name")
    assert _plugin_factory.is_plugin_registered(DummyPlugin.PLUGIN_INFO.NAME)
