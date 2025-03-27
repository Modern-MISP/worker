import asyncio
import json
from json import JSONDecodeError
from typing import Optional

import aiohttp
from celery.utils.log import get_task_logger

from mmisp.db.database import sessionmanager
from mmisp.db.models.object import ObjectTemplate, ObjectTemplateElement
from mmisp.util.async_download import download_files
from mmisp.util.github import GithubUtils
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.jobs.object_template.job_data import CreateObjectTemplatesImportData, ImportObjectTemplatesResult

_logger = get_task_logger(__name__)


@celery_app.task
def import_object_templates_job(
    user_data: UserData, data: CreateObjectTemplatesImportData
) -> ImportObjectTemplatesResult:
    """Celery task to import object templates from a GitHub repository.

    Args:
        user_data: User data required for the task.
        data: Data containing GitHub repository details and import configuration.

    Returns:
        ImportObjectTemplatesResult: Result of the import operation, including success status and any errors.
    """
    return asyncio.run(_import_object_templates_job(data))


async def _import_object_templates_job(data: CreateObjectTemplatesImportData) -> ImportObjectTemplatesResult:
    """Asynchronously imports object templates from a GitHub repository.

    Args:
        data: Data containing GitHub repository details and import configuration.

    Returns:
        ImportObjectTemplatesResult: Result of the import operation, including success status and any errors.
    """
    try:
        repo = GithubUtils(data.github_repository_name, data.github_repository_branch)
    except AttributeError:
        return ImportObjectTemplatesResult(
            success=False, error_message="Cannot access specified GitHub repository or branch"
        )

    template_list = repo.list_directories("objects")
    if not template_list:
        return ImportObjectTemplatesResult(
            success=False, error_message=f"Repository {repo.repository.name} doesn't contain 'objects' folder."
        )

    async with aiohttp.ClientSession() as session:
        pattern = repo.get_raw_url() + "{}/definition.json"
        results = await download_files(session, [pattern.format(value) for value in template_list])

    async with sessionmanager.session() as db:
        imported = []
        failed = []
        for result in results:
            template_name = result.url.path.split("/")[-2]

            if result.status != 200:
                failed.append(template_name)
                continue

            template = parse_object_template_hierarchy(result.data)
            if not template:
                failed.append(template_name)
                continue

            db.add(template)
            imported.append(template_name)

        try:
            await db.commit()
        except Exception as e:
            print(e)
            await db.rollback()
            return ImportObjectTemplatesResult(
                success=False, error_message="Database error occurred, failed to save object templates."
            )

    failed = failed if failed else None
    return ImportObjectTemplatesResult(success=True, imported_object_templates=imported, failed_object_templates=failed)


def parse_object_template_hierarchy(data: str) -> Optional[ObjectTemplate]:
    """Parses the object template hierarchy from the provided JSON data.

    Args:
        data: The JSON data representing the object template.

    Returns:
        Optional[ObjectTemplate]: The parsed ObjectTemplate object, or None if the data is invalid.
    """
    try:
        template_dict = json.loads(data)
    except JSONDecodeError:
        return None

    required = template_dict.get("required")
    required_one_of = template_dict.get("requiredOneOf")
    requirements = {}

    if required:
        requirements["required"] = required
    if required_one_of:
        requirements["requiredOneOf"] = required_one_of

    template = ObjectTemplate(
        user_id=0,
        org_id=0,
        uuid=template_dict["uuid"],
        name=template_dict["name"],
        meta_category=template_dict["meta-category"],
        description=template_dict["description"],
        version=template_dict["version"],
        requirements=requirements or None,
    )

    attributes = template_dict["attributes"]
    for element_name, element_dict in attributes.items():
        template_element = ObjectTemplateElement(
            object_relation=element_name,
            type=element_dict["misp-attribute"],
            ui_priority=element_dict["ui-priority"],
            categories=element_dict.get("categories"),
            sane_default=element_dict.get("sane_default"),
            values_list=element_dict.get("values_list"),
            description=element_dict["description"],
            disable_correlation=element_dict.get("disable_correlation"),
            multiple=element_dict.get("multiple"),
        )
        template.elements.append(template_element)

    return template
