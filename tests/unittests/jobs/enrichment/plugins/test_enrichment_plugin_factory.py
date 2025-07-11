# from mmisp.plugins.enrichment.enrichment_plugin import EnrichmentPluginType, PluginIO
# from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin import EnrichmentPlugin, EnrichmentPluginInfo
# from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import EnrichmentPluginFactory


# class TestEnrichmentPluginFactory(unittest.TestCase):
#    _plugin_factory: EnrichmentPluginFactory = EnrichmentPluginFactory()
#
#    _test_attribute: AttributeWithTagRelationship = AttributeWithTagRelationship(
#        id=1,
#        event_id=4,
#        event_uuid="c53e97d1-2202-4988-beb1-e701f25e2218",
#        object_id=3,
#        object_relation=None,
#        category="Network activity",
#        type="hostname",
#        value="www.google.com",
#        uuid="d93ada78-3538-40c4-bde9-e85dafa316f8",
#        timestamp=1718046516,
#        first_seen=1718046516,
#        last_seen=1718046516,
#        sharing_group_id=1,
#        comment="",
#        to_ids=False,
#        distribution=2,
#    )
#
#    class TestPlugin:
#        PLUGIN_INFO: EnrichmentPluginInfo = EnrichmentPluginInfo(
#            NAME="Test Plugin",
#            PLUGIN_TYPE=PluginType.ENRICHMENT,
#            DESCRIPTION="This is a test plugin.",
#            AUTHOR="John Doe",
#            VERSION="1.0",
#            ENRICHMENT_TYPE={EnrichmentPluginType.EXPANSION},
#            MISP_ATTRIBUTES=PluginIO(INPUT=["hostname", "domain"], OUTPUT=["ip-src", "ip-dst"]),
#        )
#
#        def __init__(self: Self, misp_attribute: AttributeWithTagRelationship) -> None:
#            self._misp_attribute = misp_attribute
#
#        # not used in this test
#        def run(self: Self) -> EnrichAttributeResult:
#            pass
#
#        def test_get_input(self: Self) -> AttributeWithTagRelationship:
#            return self._misp_attribute
#
#    @classmethod
#    def setUpClass(cls: Type["TestEnrichmentPluginFactory"]) -> None:
#        cls._plugin_factory.register(cls.TestPlugin)
#
#    def test_create_plugin(self: Self):
#        test_plugin_name: str = self.TestPlugin.PLUGIN_INFO.NAME
#
#        plugin: EnrichmentPlugin = self._plugin_factory.create(test_plugin_name, self._test_attribute)
#        self.assertIsInstance(plugin, self.TestPlugin)
#        test_plugin = cast(self.TestPlugin, plugin)
#        self.assertEqual(test_plugin.test_get_input(), self._test_attribute)
#        with self.assertRaises(PluginNotFound):
#            self._plugin_factory.create("random_not_existing_plugin_name", self._test_attribute)
#
#    def test_create_invalid_plugin(self: Self):
#        with patch.object(self.TestPlugin, "__init__"):
#            test_plugin_name: str = self.TestPlugin.PLUGIN_INFO.NAME
#            with self.assertRaises(NotAValidPlugin):
#                self._plugin_factory.create(test_plugin_name, self._test_attribute)
#
#    def test_get_plugin_io(self: Self):
#        plugin_info: PluginIO = self._plugin_factory.get_plugin_io(self.TestPlugin.PLUGIN_INFO.NAME)
#        self.assertEqual(plugin_info, self.TestPlugin.PLUGIN_INFO.MISP_ATTRIBUTES)
#        with self.assertRaises(PluginNotFound):
#            self._plugin_factory.get_plugin_io("random_not_existing_plugin_name")
