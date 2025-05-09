import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import text

from mmisp.db.models.object import ObjectTemplate
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.object_template.import_object_templates_job import import_object_templates_job, queue
from mmisp.worker.jobs.object_template.job_data import CreateObjectTemplatesImportData

test_repo = "Modern-MISP/test_misp_entities"


async def clean_db(db):
    qry = text("DELETE FROM object_templates")
    await db.execute(qry)
    await db.commit()


async def start_import_job(repo, branch):
    async with queue:
        job_data = CreateObjectTemplatesImportData(github_repository_name=repo, github_repository_branch=branch)
        return await import_object_templates_job.run(UserData(user_id=0), job_data)


@pytest.mark.asyncio
async def test_object_templates_import(db):
    await clean_db(db)
    result = await start_import_job(test_repo, "object_templates")
    assert result.success is True
    assert result.imported_object_templates is not None
    assert len(result.imported_object_templates) == 1
    assert result.imported_object_templates[0] == "test_name"

    object_template = await db.scalar(
        select(ObjectTemplate)
        .where(ObjectTemplate.uuid == "b61d8aa7-9a0a-4b1b-b4c4-eba26fbd9628")
        .options(selectinload(ObjectTemplate.elements))
    )
    assert object_template is not None
    assert object_template.name == "test_name"
    assert object_template.meta_category == "file"
    assert object_template.description == "test_description"
    assert object_template.version == 1
    assert object_template.requirements == {
        "required": ["test_required_1", "test_required_2"],
        "requiredOneOf": ["test_requiredOneOf_1", "test_requiredOneOf_2"],
    }
    assert len(object_template.elements) == 1

    element = object_template.elements[0]
    assert element.object_relation == "test_element"
    assert element.type == "other"
    assert element.ui_priority == 1
    assert element.categories == ["Antivirus detection", "Other"]
    assert element.sane_default == ["test_sane_default_1", "test_sane_default_2"]
    assert element.values_list == ["test_value_1", "test_value_2"]
    assert element.description == "test_element_description"
    assert element.disable_correlation is True
    assert element.multiple is True

    await db.delete(element)
    await db.delete(object_template)
    await db.commit()


@pytest.mark.asyncio
async def test_object_templates_invalid_repo_name():
    result = await start_import_job("invalid", "object_templates")
    assert result.success is False
    assert result.error_message == "Cannot access specified GitHub repository or branch"


@pytest.mark.asyncio
async def test_object_templates_invalid_branch_name():
    result = await start_import_job(test_repo, "invalid")
    assert result.success is False
    assert result.error_message == "Cannot access specified GitHub repository or branch"


@pytest.mark.asyncio
async def test_object_templates_missing_objects_folder():
    result = await start_import_job(test_repo, "object_templates_missing_objects_folder")
    assert result.success is False
    assert result.error_message == "Repository test_misp_entities doesn't contain 'objects' folder."


@pytest.mark.asyncio
async def test_object_templates_invalid_json(db):
    await clean_db(db)
    result = await start_import_job(test_repo, "object_templates_invalid_json")
    assert result.success is True
    assert result.imported_object_templates is not None
    assert result.failed_object_templates is not None
    assert len(result.imported_object_templates) == 0
    assert len(result.failed_object_templates) == 1
    assert result.failed_object_templates[0] == "test_name"
    count = await db.scalar(select(func.count()).select_from(ObjectTemplate))
    assert count == 0
