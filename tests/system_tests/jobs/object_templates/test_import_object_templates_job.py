import pytest
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from mmisp.db.models.object import ObjectTemplate
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.object_template.import_object_templates_job import import_object_templates_job
from mmisp.worker.jobs.object_template.job_data import CreateObjectTemplatesImportData

test_repo = "Modern-MISP/test_misp_entities"


def start_import_job(repo, branch):
    job_data = CreateObjectTemplatesImportData(github_repository_name=repo, github_repository_branch=branch)
    future = import_object_templates_job.delay(UserData(user_id=0), job_data)

    return future.get()


@pytest.mark.asyncio
async def test_object_templates_import(db):
    result = start_import_job(test_repo, "object_templates")
    assert result.success is True
    assert len(result.imported_object_templates) == 1
    assert result.imported_object_templates[0] == "test_name"

    object_template = await db.scalar(
        select(ObjectTemplate).where(ObjectTemplate.uuid == "test_uuid").options(selectinload(ObjectTemplate.elements))
    )
    assert object_template is not None
    assert object_template.name == "test_name"
    assert object_template.meta_category == "file"
    assert object_template.description == "test_description"
    assert object_template.version == 1
    assert (
        object_template.requirements
        == '{"required":["test_required_1","test_required_2"],"requiredOneOf":["test_requiredOneOf_1",'
        '"test_requiredOneOf_2"]}'
    )
    assert len(object_template.elements) == 1

    element = object_template.elements[0]
    assert element.object_relation == "test_element"
    assert element.type == "other"
    assert element.ui_priority == 1
    assert element.categories == '["Antivirus detection","Other"]'
    assert element.sane_default == '["test_sane_default_1","test_sane_default_2"]'
    assert element.values_list == '["test_value_1","test_value_2"]'
    assert element.description == "test_element_description"
    assert element.disable_correlation is True
    assert element.multiple is True

    await db.delete(element)
    await db.delete(object_template)
    await db.commit()


@pytest.mark.asyncio
async def test_object_templates_invalid_repo_name():
    result = start_import_job("invalid", "object_templates")
    assert result.success is False
    assert result.error_message == "Cannot access specified GitHub repository or branch"


@pytest.mark.asyncio
async def test_object_templates_invalid_branch_name():
    result = start_import_job(test_repo, "invalid")
    assert result.success is False
    assert result.error_message == "Cannot access specified GitHub repository or branch"


@pytest.mark.asyncio
async def test_object_templates_missing_objects_folder():
    result = start_import_job(test_repo, "object_templates_missing_objects_folder")
    assert result.success is False
    assert result.error_message == "Repository test_misp_entities doesn't contain 'objects' folder."


@pytest.mark.asyncio
async def test_object_templates_database_error():
    result = start_import_job(test_repo, "object_templates_database_error")
    assert result.success is False
    assert result.error_message == "Database error occurred, failed to save object templates."


@pytest.mark.asyncio
async def test_object_templates_invalid_json(db):
    result = start_import_job(test_repo, "object_templates_invalid_json")
    assert result.success is True
    assert len(result.imported_object_templates) == 0
    assert len(result.failed_object_templates) == 1
    assert result.failed_object_templates[0] == "test_name"
    count = await db.scalar(select(func.count()).select_from(ObjectTemplate))
    assert count == 0
