import httpx
from pydantic import ValidationError
from streaq import WrappedContext

from mmisp.api_schemas.object_templates import ImportObjectTemplateFile
from mmisp.db.database import sessionmanager
from mmisp.db.models.object import ObjectTemplate, ObjectTemplateElement
from mmisp.util.async_download import download_files
from mmisp.util.github import GithubUtils
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.object_template.job_data import CreateObjectTemplatesImportData, ImportObjectTemplatesResult

from .queue import queue


@queue.task()
async def import_object_templates_job(
    ctx: WrappedContext[None], user_data: UserData, data: CreateObjectTemplatesImportData
) -> ImportObjectTemplatesResult:
    """Asynchronously imports object templates from a GitHub repository.

    Args:
        data: Data containing GitHub repository details and import configuration.

    Returns:
        ImportObjectTemplatesResult: Result of the import operation, including success status and any errors.
    """

    assert sessionmanager is not None
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

    async with httpx.AsyncClient() as session:
        pattern = repo.get_raw_url() + "{}/definition.json"
        results = await download_files(session, [pattern.format(value) for value in template_list])

    async with sessionmanager.session() as db:
        imported = []
        failed = []
        for result in results:
            template_name = result.url.path.split("/")[-2]

            if result.status_code != 200:
                failed.append(template_name)
                continue

            template = parse_object_template_hierarchy(result.text)
            if not template:
                failed.append(template_name)
                continue

            db.add(template)
            imported.append(template_name)

        try:
            await db.commit()
        except Exception:
            await db.rollback()
            return ImportObjectTemplatesResult(
                success=False, error_message="Database error occurred, failed to save object templates."
            )

    failed_ret = failed if failed else None
    return ImportObjectTemplatesResult(
        success=True, imported_object_templates=imported, failed_object_templates=failed_ret
    )


def parse_object_template_hierarchy(data: str) -> ObjectTemplate | None:
    """Parses the object template hierarchy from the provided JSON data.

    Args:
        data: The JSON data representing the object template.

    Returns:
        Optional[ObjectTemplate]: The parsed ObjectTemplate object, or None if the data is invalid.
    """
    try:
        template_dict = ImportObjectTemplateFile.model_validate_json(data)
    except ValidationError as e:
        print(e)
        return None

    required = template_dict.required
    required_one_of = template_dict.requiredOneOf
    requirements = {}

    if required:
        requirements["required"] = required
    if required_one_of:
        requirements["requiredOneOf"] = required_one_of

    template = ObjectTemplate(
        user_id=0,
        org_id=0,
        uuid=template_dict.uuid,
        name=template_dict.name,
        meta_category=template_dict.meta_category,
        description=template_dict.description,
        version=template_dict.version,
        requirements=requirements or None,
    )

    attributes = template_dict.attributes
    for element_name, element_dict in attributes.items():
        template_element = ObjectTemplateElement(
            object_relation=element_name,
            type=element_dict.misp_attribute,
            ui_priority=element_dict.ui_priority,
            categories=element_dict.categories,
            sane_default=element_dict.sane_default,
            values_list=element_dict.values_list,
            description=element_dict.description,
            disable_correlation=element_dict.disable_correlation,
            multiple=element_dict.multiple,
        )
        template.elements.append(template_element)

    return template
