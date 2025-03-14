import asyncio
import json
from json import JSONDecodeError
from typing import Optional

import aiohttp
from celery.utils.log import get_task_logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.db.database import sessionmanager
from mmisp.db.models.galaxy import Galaxy
from mmisp.db.models.galaxy_cluster import GalaxyCluster, GalaxyClusterRelation, GalaxyElement
from mmisp.db.models.tag import Tag
from mmisp.util.async_download import download_files
from mmisp.util.github import GithubUtils
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.jobs.galaxy.job_data import CreateGalaxiesImportData, ImportGalaxiesResult

_logger = get_task_logger(__name__)


@celery_app.task
def import_galaxies_job(user_data: UserData, data: CreateGalaxiesImportData) -> ImportGalaxiesResult:
    """Celery task to import galaxies from a GitHub repository.

    Args:
        user_data: User data required for the task.
        data: Data containing GitHub repository details and import configuration.

    Returns:
        ImportGalaxiesResult: Result of the import operation, including success status and any errors.
    """
    return asyncio.run(_import_galaxies_job(data))


async def _import_galaxies_job(data: CreateGalaxiesImportData) -> ImportGalaxiesResult:
    """Asynchronously imports galaxies from a GitHub repository.

    Args:
        data: Data containing GitHub repository details and import configuration.

    Returns:
        ImportGalaxiesResult: Result of the import operation, including success status and any errors.
    """
    try:
        repo = GithubUtils(data.github_repository_name, data.github_repository_branch)
    except AttributeError:
        return ImportGalaxiesResult(success=False, error_message="Cannot access specified GitHub repository or branch")

    galaxy_list = repo.list_files("galaxies")
    if not galaxy_list:
        return ImportGalaxiesResult(
            success=False,
            error_message=f"Repository {repo.repository.name} doesn't contain 'galaxies' folder.",
        )

    async with aiohttp.ClientSession() as session:
        pattern = repo.get_raw_url()
        galaxies, clusters = await asyncio.gather(
            download_files(session, [pattern + value for value in galaxy_list]),
            download_files(session, [pattern + "clusters/" + value.split("/")[-1] for value in galaxy_list]),
        )

    async with sessionmanager.session() as db:
        imported = []
        failed = []
        for galaxy_resp, cluster_resp in zip(galaxies, clusters):
            filename = galaxy_resp.url.path.split("/")[-1].removesuffix(".json")
            if galaxy_resp.status != 200 or cluster_resp.status != 200:
                failed.append(filename)
                continue

            galaxy = await parse_galaxy_hierarchy(db, galaxy_resp.data, cluster_resp.data)
            if not galaxy:
                failed.append(filename)
                continue

            db.add(galaxy)
            imported.append(filename)

        try:
            await db.commit()
        except Exception:
            await db.rollback()
            return ImportGalaxiesResult(
                success=False, error_message="Database error occurred, failed to save galaxies."
            )

    failed = failed if failed else None
    return ImportGalaxiesResult(success=True, imported_galaxies=imported, failed_galaxies=failed)


def parse_galaxy_elements(elements_dict: dict) -> list[GalaxyElement]:
    """Parses galaxy elements from a dictionary.

    Args:
        elements_dict: Dictionary containing galaxy elements.

    Returns:
        list[GalaxyElement]: List of parsed GalaxyElement objects.
    """
    elements = []

    for key, value in elements_dict.items():
        if isinstance(value, list):
            for el in value:
                elements.append(GalaxyElement(key=key, value=el))
        else:
            elements.append(GalaxyElement(key=key, value=value))

    return elements


async def parse_cluster_relations(db: AsyncSession, relation_list: list) -> list[GalaxyClusterRelation]:
    """Parses galaxy cluster relations from a list.

    Args:
        db: The database session.
        relation_list: List of relations to parse.

    Returns:
        list[GalaxyClusterRelation]: List of parsed GalaxyClusterRelation objects.
    """
    relations = []

    for relation_dict in relation_list:
        uuid = relation_dict.get("dest-uuid")
        type = relation_dict.get("type")

        if not (uuid and type):
            continue

        referenced_id = await db.scalar(select(GalaxyCluster.id).where(GalaxyCluster.uuid == uuid))
        relation = GalaxyClusterRelation(
            referenced_galaxy_cluster_id=referenced_id if referenced_id else 0,
            referenced_galaxy_cluster_uuid=uuid,
            referenced_galaxy_cluster_type=type,
            distribution=3,
        )

        tag_list = relation_dict.get("tags")
        if tag_list:
            tags = await db.scalars(select(Tag).where(Tag.name.in_(tag_list)))
            relation.relation_tags.extend(tags)
        relations.append(relation)

    return relations


async def parse_galaxy_hierarchy(db: AsyncSession, galaxy_data: str, cluster_data: str) -> Optional[Galaxy]:
    """Parses the galaxy hierarchy from the provided JSON data.

    Args:
        db: The database session.
        galaxy_data: JSON data representing the galaxy.
        cluster_data: JSON data representing the galaxy clusters.

    Returns:
        Optional[Galaxy]: The parsed Galaxy object, or None if the data is invalid.
    """
    try:
        galaxy_dict = json.loads(galaxy_data)
        cluster_dict = json.loads(cluster_data)
    except JSONDecodeError:
        return None

    kill_chain_str = galaxy_dict.pop("kill_chain_order", None)
    kill_chain_order = json.dumps(kill_chain_str, separators=(",", ":")) if kill_chain_str is not None else None
    galaxy = Galaxy(**galaxy_dict, kill_chain_order=kill_chain_order, org_id=0, orgc_id=0, distribution=3)

    cluster_base_dict = {
        "collection_uuid": cluster_dict["uuid"],
        "type": cluster_dict["type"],
        "source": cluster_dict["source"],
        "authors": json.dumps(cluster_dict["authors"], separators=(",", ":")),
        "version": cluster_dict["version"],
        "distribution": 3,
    }
    tag_pattern = f'{galaxy.namespace}:{cluster_dict["type"]}="{{}}"'

    for value in cluster_dict["values"]:
        galaxy_cluster = GalaxyCluster(
            **cluster_base_dict,
            uuid=value.get("uuid"),
            value=value["value"],
            tag_name=tag_pattern.format(value["value"]),
            description=value.get("description", ""),
            deleted=value.get("revoked"),
        )
        galaxy.galaxy_clusters.append(galaxy_cluster)

        meta = value.get("meta")
        if meta:
            galaxy_elements = parse_galaxy_elements(meta)
            galaxy_cluster.galaxy_elements.extend(galaxy_elements)

        related = value.get("related")
        if related:
            cluster_relations = await parse_cluster_relations(db, related)
            for cluster_relation in cluster_relations:
                cluster_relation.galaxy_cluster_uuid = galaxy_cluster.uuid
            galaxy_cluster.cluster_relations.extend(cluster_relations)

    return galaxy
