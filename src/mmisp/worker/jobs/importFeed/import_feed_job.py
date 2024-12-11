import asyncio
import json
import re
import string
from datetime import datetime
from typing import Any

import requests
from celery.utils.log import get_task_logger
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from mmisp.db.database import sessionmanager
from mmisp.db.models.attribute import Attribute
from mmisp.db.models.event import Event
from mmisp.db.models.feed import Feed
from mmisp.db.models.object import Object
from mmisp.db.models.tag import Tag
from mmisp.lib.uuid import uuid
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.jobs.importFeed.job_data import ImportFeedData, ImportFeedResponse
from mmisp.worker.jobs.processfreetext.attribute_types.attribute_type import AttributeType
from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import (
    HashTypeValidator,
    IPTypeValidator,
    TypeValidator,
)

JOB_NAME = "import_feed_job"

validators: list[TypeValidator] = [
    IPTypeValidator(),
]

logger = get_task_logger(__name__)


def parse_site(link: str) -> str:
    """Parses a website by the given link.

    Retrieves all information from the specified website. This function
    will fetch the content of the page, extract relevant data, and return
    it as a string.

    Args:
        link (str): The URL of the website to be parsed.

    Returns:
        str: A string containing all the information fetched from the website.

    Raises:
        ValueError: If the link is not a valid URL or cannot be parsed.
        IOError: If there is an issue with fetching the website content.
    """
    try:
        response = requests.get(link)
        if response.status_code == 200:
            return response.text
        else:
            raise IOError(f"Failed to fetch content, status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        raise IOError(f"An error occurred while fetching the website: {e}")


@celery_app.task
def import_feed_job(user: UserData, data: ImportFeedData) -> ImportFeedResponse:
    """Imports a feed by a given id depending on the source format.

    This method triggers the import of a feed based on the provided id
    and the source format specified in the data. It calls an asynchronous
    helper function to perform the import job.

    Args:
        user (UserData): The user who requested the feed import.
        data (ImportFeedData): The data containing the id.

    Returns:
        ImportFeedResponse: The response indicating the result of the feed import.
    """
    return asyncio.run(_import_feed_job(user, data))


def contains(attributes: Any, attribute_to_check: Any) -> bool:
    for attribute in attributes:
        if (
            attribute.object_relation == attribute_to_check.object_relation
            and attribute.category == attribute_to_check.category
            and attribute.type == attribute_to_check.type
            and attribute.value1 == attribute_to_check.value1
            and attribute.value2 == attribute_to_check.value2
            and attribute.to_ids == attribute_to_check.to_ids
            and attribute.timestamp == attribute_to_check.timestamp
            and attribute.distribution == attribute_to_check.distribution
            and attribute.comment == attribute_to_check.comment
            and attribute.deleted == attribute_to_check.deleted
            and attribute.disable_correlation == attribute_to_check.disable_correlation
        ):
            return True
    return False


async def _import_feed_job(user: UserData, data: ImportFeedData) -> ImportFeedResponse:
    async with sessionmanager.session() as db:
        feed_to_import: Feed | None = (await db.execute(select(Feed).where(Feed.id == data.id))).scalars().first()
        logger.info("Feed chosen")
        if feed_to_import is None:
            logger.info("Feed is None")
            return ImportFeedResponse(success=False, attributes=[])
        parsed_site: str = parse_site(feed_to_import.url)
        logger.info("Site Parsed")
        attributes_list: list[Attribute] = []
        feed_event: Event | None = (
            (
                await db.execute(
                    select(Event).where(Event.id == feed_to_import.event_id).options(selectinload(Event.attributes))
                )
            )
            .scalars()
            .first()
        )
        logger.info("Event chosen")
        if feed_to_import.source_format == "misp":
            logger.info("feed format is misp")
            imported_event = await processmisp_job(user, parsed_site)
            logger.info("feed imported")
            if feed_event is None:
                feed_to_import.event_id = imported_event.id
            logger.info("event imported")
            logger.info(
                f"event attributes: id: {imported_event.id}, "
                f"info: {imported_event.info}, "
                f"uuid: {imported_event.uuid}, "
                f"org_id: {imported_event.org_id}, "
                f"orgc_id: {imported_event.orgc_id}, "
                f"analysis: {imported_event.analysis}, "
                f"distribution: {imported_event.distribution}, "
                f"threat_level_id: {imported_event.threat_level_id}, "
                f"user_id: {imported_event.user_id}, "
                f"date: {imported_event.date}, "
                f"published: {imported_event.published}, "
                f"attribute_count: {imported_event.attribute_count}, "
                f"timestamp: {imported_event.timestamp}, "
                f"sharing_group_id: {imported_event.sharing_group_id}, "
                f"proposal_email_lock: {imported_event.proposal_email_lock}, "
                f"locked: {imported_event.locked}, "
                f"publish_timestamp: {imported_event.publish_timestamp}, "
                f"sighting_timestamp: {imported_event.sighting_timestamp}, "
                f"disable_correlation: {imported_event.disable_correlation}, "
                f"extends_uuid: {imported_event.extends_uuid}, "
                f"protected: {imported_event.protected}, "
                f"feed event_id: {feed_to_import.event_id}"
            )
        elif feed_to_import.source_format == "csv":
            logger.info("feed format is csv")
            attributes_list = processcsv_job(user, parsed_site)
            logger.info("feed parsed")
            if feed_event is not None:
                logger.info("feed event is not None")
                for attribute in attributes_list:
                    if not contains(feed_event.attributes, attribute):
                        attribute.event_id = feed_event.id
                    db.add(attribute)
            else:
                logger.info("feed event is None")
                new_event = Event(
                    info="Imported from CSV feed",
                    org_id=0,
                    orgc_id=feed_to_import.orgc_id,
                    user_id=user.user_id,
                    date=datetime.utcnow(),
                    analysis=0,
                    attribute_count=attributes_list.__len__(),
                    threat_level_id=0,
                    protected=False,
                )
                db.add(new_event)
                await db.commit()
                await db.refresh(new_event)
                for attribute in attributes_list:
                    if not contains(new_event.attributes, attribute):
                        attribute.event_id = new_event.id
                        db.add(attribute)
                logger.info("new event added")
                feed_to_import.event_id = new_event.id
        await db.commit()
        logger.info("Import Feed Job completed")
        return ImportFeedResponse(success=True, attributes=attributes_list)


async def processmisp_job(user: UserData, string_to_process: str) -> Event:
    async with sessionmanager.session() as db:
        """Processes the given string and returns event found in it.

        This routine analyzes the provided string, identifies potential event
        according to the MISP format and returns it.

        Args:
            user (UserData): The user who requested the processing job.
            string_to_process (str): The string to be processed and analyzed for event.

        Returns:
            Event: Event found in the string
        Raises:
            ValueError: raised if the data format is not MISP
        """

        try:
            event_data = json.loads(string_to_process)
            if "Event" not in event_data:
                logger.error("Invalid MISP format: missing 'Event' key")
                raise ValueError("Invalid MISP format: missing 'Event' key")

            event_attributes = event_data["Event"].get("Attribute", [])
            event_tags = event_data["Event"].get("Tag", [])
            event_objects = event_data["Event"].get("Object", [])
            new_event = Event(
                info=event_data["Event"].get("info", "No info provided"),
                uuid=event_data["Event"].get("uuid", uuid),
                org_id=event_data["Event"].get("org_id", 0),
                orgc_id=event_data["Event"].get("orgc_id", 0),
                analysis=event_data["Event"].get("analysis", 0),
                distribution=event_data["Event"].get("distribution", 0),
                threat_level_id=event_data["Event"].get("threat_level_id", 0),
                user_id=user.user_id,
                date=datetime.utcnow(),
                published=event_data["Event"].get("published", False),
                attribute_count=event_data["Event"].get("attribute_count", len(event_attributes)),
                timestamp=event_data["Event"].get("timestamp", 0),
                sharing_group_id=event_data["Event"].get("sharing_group_id", 0),
                proposal_email_lock=event_data["Event"].get("proposal_email_lock", False),
                locked=event_data["Event"].get("locked", False),
                publish_timestamp=event_data["Event"].get("publish_timestamp", 0),
                sighting_timestamp=event_data["Event"].get("sighting_timestamp", 0),
                disable_correlation=event_data["Event"].get("disable_correlation", False),
                extends_uuid=event_data["Event"].get("extends_uuid", ""),
                protected=event_data["Event"].get("protected", False),
            )
            db.add(new_event)
            await db.commit()
            await db.refresh(new_event)
            for attr in event_attributes:
                attr_type = attr.get("type", "unknown")
                attr_comment = attr.get("comment", "")
                attr_uuid = attr.get("uuid", uuid)
                attr_event_id = new_event.id
                attr_object_relation = attr.get("object_relation", "")
                attr_value1 = attr.get("value1", "")
                attr_value2 = attr.get("value2", "")
                attr_to_ids = attr.get("to_ids", True)
                attr_timestamp = attr.get("timestamp", 0)
                attr_distribution = attr.get("distribution", 0)
                attr_sharing_group_id = attr.get("sharing_group_id", 0)
                attr_deleted = attr.get("deleted", False)
                attr_disable_correlation = attr.get("disable_correlation", False)
                attr_first_seen = attr.get("first_seen", 0)
                attr_last_seen = attr.get("last_seen", 0)
                attr_category = attr.get("category", "default")
                attribute = Attribute(
                    uuid=attr_uuid,
                    type=attr_type,
                    value1=attr_value1,
                    value2=attr_value2,
                    comment=attr_comment,
                    event_id=attr_event_id,
                    object_relation=attr_object_relation,
                    to_ids=attr_to_ids,
                    timestamp=attr_timestamp,
                    distribution=attr_distribution,
                    sharing_group_id=attr_sharing_group_id,
                    deleted=attr_deleted,
                    disable_correlation=attr_disable_correlation,
                    first_seen=attr_first_seen,
                    last_seen=attr_last_seen,
                    category=attr_category,
                )
                db.add(attribute)
            for obj in event_objects:
                misp_object = Object(
                    uuid=obj.get("uuid", uuid),
                    name=obj.get("name", "unknown"),
                    meta_category=obj.get("meta-category", "N/A"),
                    description=obj.get("description", ""),
                    template_uuid=obj.get("template_uuid", ""),
                    template_version=obj.get("template_version", 0),
                    event_id=new_event.id,
                    timestamp=obj.get("timestamp", 0),
                    distribution=obj.get("distribution", 0),
                    sharing_group_id=obj.get("sharing_group_id", 0),
                    comment=obj.get("comment", ""),
                    deleted=obj.get("deleted", False),
                    first_seen=obj.get("first_seen", None),
                    last_seen=obj.get("last_seen", None),
                )
                db.add(misp_object)
                for attr in obj.get("Attribute", []):
                    object_attribute = Attribute(
                        uuid=attr.get("uuid", uuid),
                        object_id=misp_object.id,
                        type=attr.get("type", "unknown"),
                        value1=attr.get("value1", ""),
                        value2=attr.get("value2", ""),
                        comment=attr.get("comment", ""),
                        event_id=new_event.id,
                        object_relation=attr.get("object_relation", ""),
                        to_ids=attr.get("to_ids", True),
                        timestamp=attr.get("timestamp", 0),
                        distribution=attr.get("distribution", 0),
                        sharing_group_id=attr.get("sharing_group_id", 0),
                        deleted=attr.get("deleted", False),
                        disable_correlation=attr.get("disable_correlation", False),
                        first_seen=attr.get("first_seen", 0),
                        last_seen=attr.get("last_seen", 0),
                        category=attr.get("category", "default"),
                    )
                    db.add(object_attribute)
            for tag in event_tags:
                misp_tag = Tag(
                    name=tag.get("name", ""),
                    colour=tag.get("colour", "#000000"),
                    exportable=tag.get("exportable", False),
                    user_id=user.user_id,
                    hide_tag=tag.get("hide_tag", False),
                    numerical_value=tag.get("numerical_value", 0),
                    is_galaxy=tag.get("is_galaxy", False),
                    is_custom_galaxy=tag.get("is_custom_galaxy", False),
                    local_only=tag.get("local_only", False),
                )
                db.add(misp_tag)
            logger.info(f"Processed Event: {new_event}")
            await db.commit()
            return new_event

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in processmisp_job: {e}")
            raise


def processcsv_job(user: UserData, string_to_process: str) -> list[Attribute]:
    """Processes the given string and returns a list of found attributes in CSV format.

    This routine analyzes the provided string, identifies potential attributes
    in CSV format, and returns them as a list of Attribute instances.

    Args:
        user (UserData): The user who requested the processing job.
        string_to_process (str): The string to be processed and analyzed for attributes.

    Returns:
        list[Attribute]: A list of found attributes in CSV format.
            Each attribute is represented as an instance of a certain Attribute.

    Raises:
        ValueError: If the provided string contains invalid data that cannot be processed.
        IOError: If there is an issue logging or accessing external resources during processing.
    """
    found_attributes: list[Attribute] = []
    word_list: list[str] = _split_text(string_to_process)
    for word in word_list:
        possible_attribute: AttributeType | None = _parse_attribute(word)
        if possible_attribute is not None:
            _possible_attribute = Attribute(
                type=possible_attribute.default_type,
                event_id=0,
                category="IP",
                value1=possible_attribute.value,
                value2=possible_attribute.value,
                comment="Imported from CSV Feed",
                first_seen=0,
                last_seen=0,
            )
            found_attributes.append(_possible_attribute)
            logger.info(f"Found attribute: {possible_attribute}")
    logger.info("finished processing csv data")
    return found_attributes


def _parse_attribute(input_str: str) -> AttributeType | None:
    """Parses the given input string and returns the found attribute if it is valid, otherwise None.

    This method checks if the input string matches any known attribute format using a
    series of validators, including an initial check for hash types. If a valid attribute
    is found, it is returned. Otherwise, None is returned.

    Args:
        input_str (str): The string to parse and validate as an attribute.

    Returns:
        AttributeType | None: The valid attribute if found, otherwise None.

    Raises:
        ValueError: If the input string is not in a valid format for any known attribute.
    """
    possible_attribute = HashTypeValidator().validate(input_str)
    if possible_attribute is not None:
        return possible_attribute
    refanged_input = _refang_input(input_str)

    for extended_validator in validators:
        possible_attribute = extended_validator.validate(refanged_input)
        if possible_attribute is not None:
            return possible_attribute
    return None


def _refang_input(input_str: str) -> str:
    """Refangs the given input string by normalizing obfuscated representations of URLs.

    This method transforms various "obfuscated" forms of URLs (e.g., hxxp -> http) into
    their standard representations, making it easier for the system to parse and process them.

    Args:
        input_str (str): The input string to refang, potentially containing obfuscated URLs.

    Returns:
        str: The refanged string with obfuscated characters replaced by their standard counterparts.
    """
    data_str: str = re.sub(r"hxxp|hxtp|htxp|meow|h\[tt\]p", "http", input_str, flags=re.IGNORECASE)
    data_str = re.sub(r"(\[\.\]|\[dot\]|\(dot\))", ".", data_str)
    data_str = re.sub(r"/\[hxxp:\/\/\]/", "http://", data_str)
    data_str = re.sub(r"/[\@]|\[at\]", "@", data_str)
    data_str = re.sub(r"/\[:\]/", ":", data_str)
    data_str.removesuffix(".")
    if re.search(r"\[.\]", data_str):
        data_str = re.sub(r"\[(.)\]", lambda match: match.group(0)[1], data_str)
    return data_str


def _split_text(input_str: str) -> list[str]:
    """Splits the given input string into a list of words by using common delimiters.

    This method breaks the input string into individual words based on spaces, commas, and hyphens.
    It ensures that punctuation (like periods) is stripped from the words, making it easier to process.

    Args:
        input_str (str): The input string to split into words.

    Returns:
        list[str]: A list of words extracted from the input string, with punctuation removed.
    """
    # using a translation_table is a bit slower on short inputs, but a lot faster on large inputs.
    delimiters = string.whitespace + "-,"
    translation_table = str.maketrans({ch: " " for ch in delimiters})
    splitted = input_str.translate(translation_table).split()
    return [w.strip(".") for w in splitted]
