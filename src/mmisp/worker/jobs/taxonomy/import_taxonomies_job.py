import asyncio
import json
from json import JSONDecodeError
from typing import Optional

import aiohttp
from aiohttp import ClientSession
from celery.utils.log import get_task_logger

from mmisp.db.database import sessionmanager
from mmisp.db.models.taxonomy import Taxonomy, TaxonomyEntry, TaxonomyPredicate
from mmisp.util.async_download import download_files
from mmisp.util.github import GithubUtils
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.jobs.taxonomy.job_data import CreateTaxonomiesImportData, ImportTaxonomiesResult

_logger = get_task_logger(__name__)


@celery_app.task
def import_taxonomies_job(user_data: UserData, data: CreateTaxonomiesImportData) -> ImportTaxonomiesResult:
    """Celery task to import taxonomies from a GitHub repository.

    Args:
        user_data: User data required for the task.
        data: Data containing GitHub repository details and import configuration.

    Returns:
        ImportTaxonomiesResult: Result of the import operation, including success status and any errors.
    """
    return asyncio.run(_import_taxonomies_job(data))


async def _import_taxonomies_job(data: CreateTaxonomiesImportData) -> ImportTaxonomiesResult:
    """Asynchronously imports taxonomies from a GitHub repository.

    Args:
        data: Data containing GitHub repository details and import configuration.

    Returns:
        ImportTaxonomiesResult: Result of the import operation, including success status and any errors.
    """
    try:
        repo = GithubUtils(data.github_repository_name, data.github_repository_branch)
    except AttributeError:
        return ImportTaxonomiesResult(
            success=False, error_message="Cannot access specified GitHub repository or branch"
        )

    async with aiohttp.ClientSession() as session:
        manifest = await fetch_manifest(session, repo)
        if not manifest:
            return ImportTaxonomiesResult(
                success=False, error_message=f"Repository {repo.repository.name} doesn't contain correct manifest file."
            )

        pattern = repo.get_raw_url() + "{}/machinetag.json"
        results = await download_files(session, [pattern.format(value["name"]) for value in manifest["taxonomies"]])

    async with sessionmanager.session() as db:
        imported = []
        failed = []
        for result in results:
            taxonomy_name = result.url.path.split("/")[-2]

            if result.status != 200:
                failed.append(taxonomy_name)
                continue

            taxonomy = parse_taxonomy_hierarchy(result.data)
            if not taxonomy:
                failed.append(taxonomy_name)
                continue

            db.add(taxonomy)
            imported.append(taxonomy_name)

        try:
            await db.commit()
        except Exception:
            await db.rollback()
            return ImportTaxonomiesResult(
                success=False, error_message="Database error occurred, failed to save taxonomies."
            )

    failed = failed if failed else None
    return ImportTaxonomiesResult(success=True, imported_taxonomies=imported, failed_taxonomies=failed)


async def fetch_manifest(session: ClientSession, repo: GithubUtils) -> Optional[dict]:
    """Fetches the manifest file from the specified GitHub repository.

    Args:
        session: The aiohttp client session.
        repo: The GitHub repository utility instance.

    Returns:
        Optional[dict]: The parsed manifest file as a dictionary, or None if the file is not found or invalid.
    """
    async with session.get(repo.get_raw_url() + "MANIFEST.json") as response:
        if response.status != 200:
            return None
        try:
            return json.loads(await response.text())
        except JSONDecodeError:
            return None


def parse_taxonomy_hierarchy(data: str) -> Optional[Taxonomy]:
    """Parses the taxonomy hierarchy from the provided JSON data.

    Args:
        data: The JSON data representing the taxonomy.

    Returns:
        Optional[Taxonomy]: The parsed Taxonomy object, or None if the data is invalid.
    """
    try:
        taxonomy_dict = json.loads(data)
    except JSONDecodeError:
        return None

    taxonomy = Taxonomy(
        namespace=taxonomy_dict["namespace"],
        description=taxonomy_dict["description"],
        version=taxonomy_dict["version"],
        exclusive=taxonomy_dict.get("exclusive"),
    )

    values = taxonomy_dict.get("values")
    values_index = {el["predicate"]: el.get("entry") for el in values} if values else {}

    for predicate_dict in taxonomy_dict["predicates"]:
        predicate = TaxonomyPredicate(**predicate_dict)
        taxonomy.predicates.append(predicate)

        entries = values_index.get(predicate_dict["value"])
        if entries:
            for entry_dict in entries:
                entry = TaxonomyEntry(**entry_dict)
                predicate.entries.append(entry)

    return taxonomy
