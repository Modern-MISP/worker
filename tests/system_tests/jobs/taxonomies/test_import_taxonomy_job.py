import pytest
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from mmisp.db.models.taxonomy import Taxonomy, TaxonomyPredicate
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.taxonomy.import_taxonomies_job import import_taxonomies_job
from mmisp.worker.jobs.taxonomy.job_data import CreateTaxonomiesImportData

test_repo = "Modern-MISP/test_misp_entities"


def start_import_job(repo, branch):
    job_data = CreateTaxonomiesImportData(github_repository_name=repo, github_repository_branch=branch)
    future = import_taxonomies_job.delay(UserData(user_id=0), job_data)

    return future.get()


@pytest.mark.asyncio
async def test_taxonomies_import(db):
    result = start_import_job(test_repo, "taxonomies")
    assert result.success is True
    assert len(result.imported_taxonomies) == 1
    assert result.imported_taxonomies[0] == "test_namespace"

    taxonomy = await db.scalar(
        select(Taxonomy)
        .where(Taxonomy.namespace == "test_namespace")
        .options(selectinload(Taxonomy.predicates).selectinload(TaxonomyPredicate.entries))
    )
    assert taxonomy is not None
    assert taxonomy.description == "test_description"
    assert taxonomy.version == 1
    assert taxonomy.exclusive is True
    assert len(taxonomy.predicates) == 1

    predicate = taxonomy.predicates[0]
    assert predicate.value == "test_predicate_value"
    assert predicate.expanded == "test_predicate_expanded"
    assert predicate.colour == "test_pc"
    assert predicate.description == "test_predicate_description"
    assert predicate.exclusive is True
    assert predicate.numerical_value == 1
    assert len(predicate.entries) == 1

    entry = predicate.entries[0]
    assert entry.value == "test_entry_value"
    assert entry.expanded == "test_entry_expanded"
    assert entry.colour == "test_ec"
    assert entry.description == "test_entry_description"
    assert entry.numerical_value == 1

    await db.delete(entry)
    await db.delete(predicate)
    await db.delete(taxonomy)
    await db.commit()


@pytest.mark.asyncio
async def test_taxonomies_import_predicate_only(db):
    result = start_import_job(test_repo, "taxonomies_predicate_only")
    assert result.success is True
    assert len(result.imported_taxonomies) == 1
    assert result.imported_taxonomies[0] == "test_namespace"

    taxonomy = await db.scalar(
        select(Taxonomy)
        .where(Taxonomy.namespace == "test_namespace")
        .options(selectinload(Taxonomy.predicates).selectinload(TaxonomyPredicate.entries))
    )
    assert taxonomy is not None
    assert taxonomy.description == "test_description"
    assert taxonomy.version == 1
    assert taxonomy.exclusive is True
    assert len(taxonomy.predicates) == 1

    predicate = taxonomy.predicates[0]
    assert predicate.value == "test_predicate_value"
    assert predicate.expanded == "test_predicate_expanded"
    assert predicate.colour == "test_pc"
    assert predicate.description == "test_predicate_description"
    assert predicate.exclusive is True
    assert predicate.numerical_value == 1
    assert len(predicate.entries) == 0

    await db.delete(predicate)
    await db.delete(taxonomy)
    await db.commit()


@pytest.mark.asyncio
async def test_taxonomies_invalid_repo_name():
    result = start_import_job("invalid", "taxonomies")
    assert result.success is False
    assert result.error_message == "Cannot access specified GitHub repository or branch"


@pytest.mark.asyncio
async def test_taxonomies_invalid_branch_name():
    result = start_import_job(test_repo, "invalid")
    assert result.success is False
    assert result.error_message == "Cannot access specified GitHub repository or branch"


@pytest.mark.asyncio
async def test_taxonomies_missing_manifest():
    result = start_import_job(test_repo, "taxonomies_missing_manifest")
    assert result.success is False
    assert result.error_message == "Repository test_misp_entities doesn't contain correct manifest file."


@pytest.mark.asyncio
async def test_taxonomies_database_error():
    result = start_import_job(test_repo, "taxonomies_database_error")
    assert result.success is False
    assert result.error_message == "Database error occurred, failed to save taxonomies."


@pytest.mark.asyncio
async def test_taxonomies_invalid_json(db):
    result = start_import_job(test_repo, "taxonomies_invalid_json")
    assert result.success is True
    assert len(result.imported_taxonomies) == 0
    assert len(result.failed_taxonomies) == 1
    assert result.failed_taxonomies[0] == "test_namespace"
    count = await db.scalar(select(func.count()).select_from(Taxonomy))
    assert count == 0


@pytest.mark.asyncio
async def test_taxonomies_missing_taxonomy(db):
    result = start_import_job(test_repo, "taxonomies_missing_taxonomy")
    assert result.success is True
    assert len(result.imported_taxonomies) == 0
    assert len(result.failed_taxonomies) == 1
    assert result.failed_taxonomies[0] == "test_namespace"
    count = await db.scalar(select(func.count()).select_from(Taxonomy))
    assert count == 0
