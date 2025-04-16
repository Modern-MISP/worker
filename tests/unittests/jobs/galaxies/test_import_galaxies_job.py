import pytest
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from mmisp.db.models.galaxy import Galaxy
from mmisp.db.models.galaxy_cluster import GalaxyCluster
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.galaxy.import_galaxies_job import import_galaxies_job, queue
from mmisp.worker.jobs.galaxy.job_data import CreateGalaxiesImportData

test_repo = "Modern-MISP/test_misp_entities"


async def start_import_job(repo, branch):
    async with queue:
        job_data = CreateGalaxiesImportData(github_repository_name=repo, github_repository_branch=branch)
        return await import_galaxies_job.run(UserData(user_id=0), job_data)


@pytest.mark.asyncio
async def test_galaxies_import(db):
    result = await start_import_job(test_repo, "galaxies")
    assert result.success is True
    assert result.imported_galaxies is not None
    assert len(result.imported_galaxies) == 1
    assert result.imported_galaxies[0] == "test_galaxy"

    galaxy = await db.scalar(
        select(Galaxy)
        .where(Galaxy.uuid == "test_galaxy_uuid")
        .options(selectinload(Galaxy.galaxy_clusters).selectinload(GalaxyCluster.galaxy_elements))
    )
    assert galaxy is not None
    assert galaxy.uuid == "test_galaxy_uuid"
    assert galaxy.name == "test_name"
    assert galaxy.type == "test_galaxy"
    assert galaxy.description == "test_galaxy_description"
    assert galaxy.version == "1"
    assert galaxy.icon == "test_icon"
    assert galaxy.namespace == "test_namespace"
    assert galaxy.kill_chain_order == '{"test_kill_chain":["test_value_1","test_value_2"]}'
    assert len(galaxy.galaxy_clusters) == 1

    cluster = galaxy.galaxy_clusters[0]
    assert cluster.uuid == "test_cluster_uuid"
    assert cluster.collection_uuid == "test_cluster_collection_uuid"
    assert cluster.type == "test_galaxy"
    assert cluster.value == "test_value"
    assert cluster.tag_name == 'test_namespace:test_galaxy="test_value"'
    assert cluster.description == "test_cluster_description"
    assert cluster.source == "test_source"
    assert cluster.authors == ["test_author_1", "test_author_2"]
    assert cluster.version == 1
    assert cluster.distribution == 3
    assert cluster.deleted == 1
    assert len(cluster.galaxy_elements) == 3

    values = [("type", "test_type_1"), ("type", "test_type_2"), ("complexity", "test_complexity")]
    elements = list(cluster.galaxy_elements)

    for value in values:
        for i, element in enumerate(elements):
            if element.key == value[0] and element.value == value[1]:
                elements.pop(i)
                break
    assert len(elements) == 0, "Some galaxy elements are missing"

    for el in cluster.galaxy_elements:
        await db.delete(el)
    await db.delete(cluster)
    await db.delete(galaxy)
    await db.commit()


@pytest.mark.asyncio
async def test_galaxies_related(db):
    result = await start_import_job(test_repo, "galaxies_related")
    assert result.success is True
    assert result.imported_galaxies is not None
    assert len(result.imported_galaxies) == 1
    assert result.imported_galaxies[0] == "test_galaxy"

    galaxy = await db.scalar(
        select(Galaxy)
        .where(Galaxy.uuid == "test_galaxy_uuid")
        .options(selectinload(Galaxy.galaxy_clusters).selectinload(GalaxyCluster.cluster_relations))
    )
    assert galaxy is not None
    assert len(galaxy.galaxy_clusters) == 2

    referenced_cluster = galaxy.galaxy_clusters[0]
    referencing_cluster = galaxy.galaxy_clusters[1]

    if len(referencing_cluster.cluster_relations) != 1:
        referencing_cluster, referenced_cluster = referenced_cluster, referencing_cluster

    assert len(referencing_cluster.cluster_relations) == 1

    relation = referencing_cluster.cluster_relations[0]
    assert relation.galaxy_cluster_id == referencing_cluster.id
    assert relation.galaxy_cluster_uuid == "test_cluster_uuid_2"
    assert relation.referenced_galaxy_cluster_uuid == "test_cluster_uuid_1"
    assert relation.referenced_galaxy_cluster_type == "test_type"

    await db.delete(relation)
    await db.delete(referencing_cluster)
    await db.delete(referenced_cluster)
    await db.delete(galaxy)
    await db.commit()


@pytest.mark.asyncio
async def test_galaxies_invalid_repo_name():
    result = await start_import_job("invalid", "galaxies")
    assert result.success is False
    assert result.error_message == "Cannot access specified GitHub repository or branch"


@pytest.mark.asyncio
async def test_galaxies_invalid_branch_name():
    result = await start_import_job(test_repo, "invalid")
    assert result.success is False
    assert result.error_message == "Cannot access specified GitHub repository or branch"


@pytest.mark.asyncio
async def test_galaxies_missing_galaxies_folder():
    result = await start_import_job(test_repo, "galaxies_missing_galaxies_folder")
    assert result.success is False
    assert result.error_message == "Repository test_misp_entities doesn't contain 'galaxies' folder."


@pytest.mark.asyncio
async def test_galaxies_database_error():
    result = await start_import_job(test_repo, "galaxies_database_error")
    assert result.success is False
    assert result.error_message == "Database error occurred, failed to save galaxies."


@pytest.mark.asyncio
async def test_galaxies_missing_cluster(db):
    result = await start_import_job(test_repo, "galaxies_missing_cluster")
    assert result.success is True
    assert result.imported_galaxies is not None
    assert result.failed_galaxies is not None
    assert len(result.imported_galaxies) == 0
    assert len(result.failed_galaxies) == 1
    assert result.failed_galaxies[0] == "test_galaxy"
    count = await db.scalar(select(func.count()).select_from(Galaxy))
    assert count == 0


@pytest.mark.asyncio
async def test_galaxies_invalid_galaxy_json(db):
    result = await start_import_job(test_repo, "galaxies_invalid_galaxy_json")
    assert result.success is True
    assert result.imported_galaxies is not None
    assert result.failed_galaxies is not None
    assert len(result.imported_galaxies) == 0
    assert len(result.failed_galaxies) == 1
    assert result.failed_galaxies[0] == "test_galaxy"
    count = await db.scalar(select(func.count()).select_from(Galaxy))
    assert count == 0


@pytest.mark.asyncio
async def test_galaxies_invalid_cluster_json(db):
    result = await start_import_job(test_repo, "galaxies_invalid_cluster_json")
    assert result.success is True
    assert result.imported_galaxies is not None
    assert result.failed_galaxies is not None
    assert len(result.imported_galaxies) == 0
    assert len(result.failed_galaxies) == 1
    assert result.failed_galaxies[0] == "test_galaxy"
    count = await db.scalar(select(func.count()).select_from(Galaxy))
    assert count == 0
