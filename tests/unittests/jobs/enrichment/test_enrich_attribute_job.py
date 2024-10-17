import asyncio
from typing import Self
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from mmisp.api_schemas.attributes import AddAttributeBody, GetAttributeAttributes
from mmisp.lib.uuid import uuid
from mmisp.plugins.enrichment.data import EnrichAttributeResult, NewAttribute, NewTag
from mmisp.plugins.enrichment.enrichment_plugin import EnrichmentPluginInfo, EnrichmentPluginType, PluginIO
from mmisp.plugins.models.attribute import AttributeWithTagRelationship
from mmisp.plugins.plugin_type import PluginType
from mmisp.tests.generators.attribute_generator import (
    generate_attribute_with_tag_relationship,
    generate_get_attribute_attributes_response,
)
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.exceptions.job_exceptions import JobException
from mmisp.worker.exceptions.misp_api_exceptions import APIException
from mmisp.worker.jobs.enrichment import enrich_attribute_job
from mmisp.worker.jobs.enrichment.enrichment_worker import enrichment_worker
from mmisp.worker.jobs.enrichment.job_data import EnrichAttributeData
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin import EnrichmentPlugin
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import enrichment_plugin_factory
from mmisp.worker.jobs.enrichment.utility import parse_attribute_with_tag_relationship
from mmisp.worker.misp_database.misp_api import MispAPI


class _TestPlugin:
    PLUGIN_INFO: EnrichmentPluginInfo = EnrichmentPluginInfo(
        NAME="TestEnrichAttributeJob-Plugin",
        PLUGIN_TYPE=PluginType.ENRICHMENT,
        DESCRIPTION="This is a test plugin.",
        AUTHOR="John Doe",
        VERSION="1.0",
        ENRICHMENT_TYPE={EnrichmentPluginType.EXPANSION},
        MISP_ATTRIBUTES=PluginIO(INPUT=["hostname", "domain"], OUTPUT=["ip-src", "ip-dst"]),
    )

    TEST_PLUGIN_RESULT: EnrichAttributeResult = EnrichAttributeResult(
        attributes=[
            NewAttribute(
                attribute=AddAttributeBody(
                    event_id=815,
                    object_id=24,
                    category="Network activity",
                    type="domain",
                    value="www.kit.edu",
                    distribution=2,
                )
            )
        ],
        event_tags=[NewTag(tag_id=3)],
    )

    def __init__(self: Self, misp_attribute: AttributeWithTagRelationship) -> None:
        self.__misp_attribute = misp_attribute

    def run(self: Self) -> EnrichAttributeResult:
        return self.TEST_PLUGIN_RESULT


class _TestPluginTwo:
    PLUGIN_INFO: EnrichmentPluginInfo = EnrichmentPluginInfo(
        NAME="TestEnrichAttributeJob-PluginTwo",
        PLUGIN_TYPE=PluginType.ENRICHMENT,
        DESCRIPTION="This is a test plugin.",
        AUTHOR="John Doe",
        VERSION="1.0",
        ENRICHMENT_TYPE={EnrichmentPluginType.EXPANSION},
        MISP_ATTRIBUTES=PluginIO(INPUT=["domain", "ip-dst"], OUTPUT=["ip-src"]),
    )
    TEST_PLUGIN_RESULT: EnrichAttributeResult = EnrichAttributeResult(
        attributes=[
            NewAttribute(
                attribute=AddAttributeBody(
                    event_id=816,
                    object_id=24,
                    category="Network activity",
                    type="domain",
                    value="www.kit.edu",
                    distribution=2,
                )
            )
        ],
        event_tags=[NewTag(tag_id=4)],
    )

    def __init__(self: Self, misp_attribute: AttributeWithTagRelationship) -> None:
        self.__misp_attribute = misp_attribute

    def run(self: Self) -> EnrichAttributeResult:
        return self.TEST_PLUGIN_RESULT


def _generate_plugin_mock(misp_attributes: PluginIO) -> Mock:
    plugin_mock_info: EnrichmentPluginInfo = EnrichmentPluginInfo(
        NAME=uuid(),
        PLUGIN_TYPE=PluginType.ENRICHMENT,
        DESCRIPTION="This is a test plugin.",
        AUTHOR="John Doe",
        VERSION="1.0",
        ENRICHMENT_TYPE={EnrichmentPluginType.EXPANSION},
        MISP_ATTRIBUTES=misp_attributes
    )

    plugin_mock: Mock = Mock(spec=EnrichmentPlugin)
    plugin_mock.PLUGIN_INFO = plugin_mock_info
    plugin_mock.return_value = plugin_mock
    plugin_mock.run.return_value = EnrichAttributeResult()

    enrichment_plugin_factory.register(plugin_mock)

    return plugin_mock


@patch("mmisp.worker.jobs.enrichment.enrich_attribute_job.enrichment_worker")
@patch("mmisp.worker.misp_database.misp_sql")
def test_enrich_attribute_job(sql_mock, enrichment_worker_mock):
    api_mock = Mock(spec=MispAPI)
    enrichment_worker_mock.misp_api = api_mock

    attribute: GetAttributeAttributes = generate_get_attribute_attributes_response()
    api_mock.get_attribute.return_value = attribute
    sql_mock.get_attribute_tag_id.return_value = 1

    plugin_mock: Mock = _generate_plugin_mock(PluginIO(INPUT=[attribute.type], OUTPUT=[attribute.type]))
    plugin_mock_name = plugin_mock.PLUGIN_INFO.NAME

    job_data: EnrichAttributeData = EnrichAttributeData(
        attribute_id=attribute.id, enrichment_plugins=[plugin_mock_name]
    )

    pseudo_result_attribute: AddAttributeBody = AddAttributeBody(type=attribute.type)
    plugin_mock_result: EnrichAttributeResult = EnrichAttributeResult(
        attributes=[NewAttribute(attribute=pseudo_result_attribute)])
    plugin_mock.run.return_value = plugin_mock_result

    job_result: EnrichAttributeResult
    with patch.object(
            enrichment_plugin_factory, 'create') as create_plugin_mock:
        create_plugin_mock.return_value = plugin_mock
        job_result: EnrichAttributeResult = enrich_attribute_job.enrich_attribute_job(
            UserData(user_id=0),
            job_data)

    enrichment_plugin_factory.unregister(plugin_mock_name)

    attribute_with_tag_relationship: AttributeWithTagRelationship = asyncio.run(
        parse_attribute_with_tag_relationship(attribute))

    plugin_mock.assert_called_once_with(attribute_with_tag_relationship)
    assert job_result.attributes[0].attribute == pseudo_result_attribute


def test_enrich_attribute():
    enrichment_plugin_factory.register(_TestPlugin)
    enrichment_plugin_factory.register(_TestPluginTwo)

    attribute: AttributeWithTagRelationship = generate_attribute_with_tag_relationship()
    attribute.type = "domain"

    plugins_to_execute: list[str] = [_TestPlugin.PLUGIN_INFO.NAME, _TestPluginTwo.PLUGIN_INFO.NAME]
    result: EnrichAttributeResult = enrich_attribute_job.enrich_attribute(
        attribute, plugins_to_execute
    )

    created_attributes: list[NewAttribute] = result.attributes
    created_event_tags: list[NewTag] = result.event_tags

    expected_attributes: list[NewAttribute] = (
            _TestPlugin.TEST_PLUGIN_RESULT.attributes + _TestPluginTwo.TEST_PLUGIN_RESULT.attributes
    )

    expected_event_tags: list[NewTag] = (
            _TestPlugin.TEST_PLUGIN_RESULT.event_tags + _TestPluginTwo.TEST_PLUGIN_RESULT.event_tags
    )

    assert len(created_attributes) == len(expected_attributes)
    assert all(expected_attribute in created_attributes for expected_attribute in expected_attributes)

    assert len(created_event_tags) == len(expected_event_tags)
    assert all(expected_event_tag in created_event_tags for expected_event_tag in expected_event_tags)


def test_enrich_attribute_with_faulty_plugins():
    attribute: AttributeWithTagRelationship = generate_attribute_with_tag_relationship()

    plugin_one: Mock = _generate_plugin_mock(PluginIO(INPUT=[attribute.type], OUTPUT=[attribute.type]))
    plugin_two: Mock = _generate_plugin_mock(PluginIO(INPUT=[attribute.type], OUTPUT=[attribute.type]))
    plugin_three: Mock = _generate_plugin_mock(PluginIO(INPUT=[attribute.type], OUTPUT=[attribute.type]))

    plugins_to_execute: list[str] = [
        uuid(),  # Unknown plugin
        plugin_one.PLUGIN_INFO.NAME,
        plugin_two.PLUGIN_INFO.NAME,
        plugin_three.PLUGIN_INFO.NAME
    ]

    plugin_one.side_effect = Exception("Plugin could not be instantiated.")
    plugin_two.run.side_effect = TypeError("Any error in plugin execution.")

    pseudo_result_attribute: AddAttributeBody = AddAttributeBody(type=attribute.type)
    plugin_three_result: EnrichAttributeResult = EnrichAttributeResult(
        attributes=[NewAttribute(attribute=pseudo_result_attribute)])
    plugin_three.run.return_value = plugin_three_result

    result: EnrichAttributeResult = enrich_attribute_job.enrich_attribute(attribute, plugins_to_execute)

    assert plugin_one.called
    assert plugin_two.run.called
    assert plugin_three.run.called

    assert result.attributes[0].attribute == pseudo_result_attribute


def test_enrich_attribute_skipping_plugins():
    attribute: AttributeWithTagRelationship = generate_attribute_with_tag_relationship()

    compatible_plugin: Mock = _generate_plugin_mock(PluginIO(INPUT=[attribute.type], OUTPUT=[attribute.type]))
    non_compatible_plugin: Mock = _generate_plugin_mock(
        PluginIO(INPUT=[attribute.type + "a"], OUTPUT=[attribute.type + "a"]))

    enrichment_plugin_factory.register(compatible_plugin)
    enrichment_plugin_factory.register(non_compatible_plugin)

    plugins_to_execute: list[str] = [compatible_plugin.PLUGIN_INFO.NAME, non_compatible_plugin.PLUGIN_INFO.NAME]
    enrich_attribute_job.enrich_attribute(attribute, plugins_to_execute)

    # Check that only plugins are executed that are compatible with the attribute.
    assert compatible_plugin.run.called
    assert non_compatible_plugin.run.not_called


def test_enrich_attribute_job_api_exceptions():
    with patch.object(enrichment_worker.misp_api, "get_event_attributes") as misp_api_mock:
        for exception in [APIException, HTTPException]:
            misp_api_mock.side_effect = exception("")
            with pytest.raises(JobException):
                enrich_attribute_job.enrich_attribute_job(
                    UserData(user_id=1),
                    EnrichAttributeData(attribute_id=1, enrichment_plugins=[_TestPlugin.PLUGIN_INFO.NAME])
                )
