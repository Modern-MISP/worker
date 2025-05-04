import pytest
from plugins.enrichment_plugins import dns_resolver, dummy_plugin  # noqa
from plugins.enrichment_plugins.dns_resolver import DNSResolverPlugin
from plugins.enrichment_plugins.dummy_plugin import DummyPlugin

from mmisp.plugins import factory
from mmisp.plugins.exceptions import NoValidPlugin, PluginNotFound, PluginRegistrationError
from mmisp.plugins.types import PluginType


class InvalidPlugin:
    pass


class DummyPluginClone(DummyPlugin):
    pass


def test_register():
    factory.unregister(DummyPlugin.PLUGIN_TYPE, DummyPlugin.NAME)

    instance_plugin = DummyPlugin()
    factory.register(instance_plugin)
    assert instance_plugin in factory._plugins[PluginType.ENRICHMENT.value].values()


def test_register_invalid_plugin():
    with pytest.raises(NoValidPlugin):
        factory.register(InvalidPlugin())  # type: ignore


def test_register_existing_plugin_name():
    with pytest.raises(PluginRegistrationError):
        factory.register(DummyPluginClone())


def test_unregister():
    factory.unregister(DummyPlugin.PLUGIN_TYPE, DummyPlugin.NAME)
    dummy_plugin_name: str = DummyPlugin.NAME
    factory.register(DummyPlugin())
    assert factory.is_plugin_registered(PluginType.ENRICHMENT, dummy_plugin_name)

    factory.unregister(PluginType.ENRICHMENT, DummyPlugin.NAME)

    assert not factory.is_plugin_registered(PluginType.ENRICHMENT, dummy_plugin_name)

    with pytest.raises(PluginNotFound):
        factory.unregister(PluginType.ENRICHMENT, "random_not_existing_plugin_name")
    factory.register(DummyPlugin())


def test_get_plugins():
    #    factory.register(dummy_plugin())
    #    factory.register(dns_resolver())
    loaded_plugins = factory.get_plugins(PluginType.ENRICHMENT)
    assert any(isinstance(x, DummyPlugin) for x in loaded_plugins)
    assert any(isinstance(x, DNSResolverPlugin) for x in loaded_plugins)


def test_is_plugin_registered():
    assert not factory.is_plugin_registered(PluginType.ENRICHMENT, "")
    assert not factory.is_plugin_registered(PluginType.ENRICHMENT, "random_not_existing_plugin_name")
    assert factory.is_plugin_registered(PluginType.ENRICHMENT, DummyPlugin.NAME)
