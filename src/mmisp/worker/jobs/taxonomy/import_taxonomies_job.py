import logging
from json import JSONDecodeError
from typing import Optional

from httpx import AsyncClient
from pydantic import ValidationError
from streaq import WrappedContext

from mmisp.api_schemas.taxonomies import ImportTaxonomyFile
from mmisp.db.database import sessionmanager
from mmisp.db.models.taxonomy import Taxonomy, TaxonomyEntry, TaxonomyPredicate
from mmisp.util.async_download import download_files
from mmisp.util.github import GithubUtils
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.taxonomy.job_data import CreateTaxonomiesImportData, ImportTaxonomiesResult

from .queue import queue

_logger = logging.getLogger("mmisp")


@queue.task()
async def import_taxonomies_job(
    ctx: WrappedContext[None], user_data: UserData, data: CreateTaxonomiesImportData
) -> ImportTaxonomiesResult:
    """Asynchronously imports taxonomies from a GitHub repository.

    Args:
        data: Data containing GitHub repository details and import configuration.

    Returns:
        ImportTaxonomiesResult: Result of the import operation, including success status and any errors.
    """
    assert sessionmanager is not None
    try:
        repo = GithubUtils(data.github_repository_name, data.github_repository_branch)
    except AttributeError:
        return ImportTaxonomiesResult(
            success=False, error_message="Cannot access specified GitHub repository or branch"
        )

    async with AsyncClient() as session:
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

            if result.status_code != 200:
                failed.append(taxonomy_name)
                continue

            taxonomy = parse_taxonomy_hierarchy(result.text)
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

    failed_ret = failed if failed else None
    return ImportTaxonomiesResult(success=True, imported_taxonomies=imported, failed_taxonomies=failed_ret)


async def fetch_manifest(session: AsyncClient, repo: GithubUtils) -> Optional[dict]:
    """Fetches the manifest file from the specified GitHub repository.

    Args:
        session: The httpx AsyncClient.
        repo: The GitHub repository utility instance.

    Returns:
        Optional[dict]: The parsed manifest file as a dictionary, or None if the file is not found or invalid.
    """
    response = await session.get(repo.get_raw_url() + "MANIFEST.json")
    if response.status_code != 200:
        return None
    try:
        return response.json()
    except JSONDecodeError:
        return None


def parse_taxonomy_hierarchy(data: str) -> Taxonomy | None:
    """Parses the taxonomy hierarchy from the provided JSON data.

    Args:
        data: The JSON data representing the taxonomy.

    Returns:
        Optional[Taxonomy]: The parsed Taxonomy object, or None if the data is invalid.
    """
    try:
        taxonomy_model = ImportTaxonomyFile.model_validate_json(data)
    except ValidationError:
        _logger.exception("Validation Error while parsing taxonomy file")
        return None

    taxonomy = Taxonomy(
        namespace=taxonomy_model.namespace,
        description=taxonomy_model.description,
        version=taxonomy_model.version,
        exclusive=taxonomy_model.exclusive,
    )

    values = taxonomy_model.values
    values_index = {el.predicate: el.entry for el in values} if values else {}

    for predicate_dict in taxonomy_model.predicates:
        predicate = TaxonomyPredicate(
            value=predicate_dict.value,
            expanded=predicate_dict.expanded,
            colour=predicate_dict.colour,
            description=predicate_dict.description,
            exclusive=predicate_dict.exclusive,
            numerical_value=predicate_dict.numerical_value,
        )
        taxonomy.predicates.append(predicate)

        entries = values_index.get(predicate_dict.value)
        if entries:
            for entry_dict in entries:
                entry = TaxonomyEntry(
                    value=entry_dict.value,
                    expanded=entry_dict.expanded,
                    colour=entry_dict.colour,
                    description=entry_dict.description,
                    numerical_value=entry_dict.numerical_value,
                )
                predicate.entries.append(entry)

    return taxonomy
