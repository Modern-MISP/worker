"""Mock helpers for GitHub-dependent import job tests.

These tests previously hit the real GitHub API (Modern-MISP/test_misp_entities).
CI runners cannot reach GitHub, so we mock GithubUtils and download_files.
"""

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock


def _make_response(url: str, text: str, status_code: int = 200):
    """Create a mock response object with .url.path, .status_code, .text, and .json()."""

    def _json():
        return json.loads(text) if text else None

    return SimpleNamespace(
        url=SimpleNamespace(path=url),
        status_code=status_code,
        text=text,
        json=_json,
    )


class MockGithubUtils:
    """Drop-in replacement for mmisp.util.github.GithubUtils."""

    _GITHUB_RAW_TEMPLATE = "https://raw.githubusercontent.com/{}/refs/heads/{}/"

    BRANCH_DATA: dict[str, dict] = {
        "galaxies": {
            "list_files": ["galaxies/test_galaxy.json"],
            "list_directories": ["objects/test_name"],
            "manifest": None,
            "galaxy_json": {
                "uuid": "0179fb98-9a25-403a-bbcf-17876dbe7339",
                "name": "test_name",
                "type": "test_galaxy",
                "description": "test_galaxy_description",
                "version": 1,
                "icon": "test_icon",
                "namespace": "test_namespace",
                "kill_chain_order": {"test_kill_chain": ["test_value_1", "test_value_2"]},
            },
            "cluster_json": {
                "uuid": "0179fb98-9a25-403a-bbcf-17876dbe7339",
                "name": "test_name",
                "type": "test_galaxy",
                "description": "test_galaxy_description",
                "version": 1,
                "authors": ["test_author_1", "test_author_2"],
                "source": "test_source",
                "category": "test_category",
                "values": [
                    {
                        "value": "test_value",
                        "uuid": "e2ccd6c9-e9bd-4899-abbb-8a3e69e8c86c",
                        "description": "test_cluster_description",
                        "revoked": True,
                        "meta": {
                            "type": ["test_type_1", "test_type_2"],
                            "complexity": "test_complexity",
                        },
                    }
                ],
            },
        },
        "galaxies_related": {
            "list_files": ["galaxies/test_galaxy.json"],
            "list_directories": ["objects/test_name"],
            "manifest": None,
            "galaxy_json": {
                "uuid": "0700546e-affa-4c39-9e4d-037aab88f2a5",
                "name": "test_name",
                "type": "test_galaxy",
                "description": "test_galaxy_description",
                "version": 1,
            },
            "cluster_json": {
                "uuid": "0700546e-affa-4c39-9e4d-037aab88f2a5",
                "name": "test_name",
                "type": "test_galaxy",
                "description": "test_galaxy_description",
                "version": 1,
                "authors": ["test_author"],
                "source": "test_source",
                "category": "test_category",
                "values": [
                    {
                        "value": "referenced_value",
                        "uuid": "1203d8ac-2d6e-45fc-aa56-22ee9ac3f767",
                        "description": "referenced cluster",
                    },
                    {
                        "value": "referencing_value",
                        "uuid": "e1864d08-d33d-429e-9b0d-0bafc4918acc",
                        "description": "referencing cluster",
                        "related": [
                            {
                                "dest-uuid": "1203d8ac-2d6e-45fc-aa56-22ee9ac3f767",
                                "type": "test_type",
                            }
                        ],
                    },
                ],
            },
        },
        "galaxies_missing_galaxies_folder": {
            "list_files": [],
            "list_directories": ["objects/test_name"],
            "manifest": None,
        },
        "galaxies_missing_cluster": {
            "list_files": ["galaxies/test_galaxy.json"],
            "list_directories": ["objects/test_name"],
            "manifest": None,
            "galaxy_json": {
                "uuid": "0179fb98-9a25-403a-bbcf-17876dbe7339",
                "name": "test_name",
                "type": "test_galaxy",
                "description": "test_galaxy_description",
                "version": 1,
            },
            "cluster_json": None,
        },
        "galaxies_invalid_galaxy_json": {
            "list_files": ["galaxies/test_galaxy.json"],
            "list_directories": ["objects/test_name"],
            "manifest": None,
            "galaxy_json": "not-valid-json{{{",
            "cluster_json": {
                "uuid": "0179fb98-9a25-403a-bbcf-17876dbe7339",
                "name": "test_name",
                "type": "test_galaxy",
                "description": "test_galaxy_description",
                "version": 1,
                "authors": ["test_author"],
                "source": "test_source",
                "category": "test_category",
                "values": [
                    {
                        "value": "test_value",
                        "uuid": "e2ccd6c9-e9bd-4899-abbb-8a3e69e8c86c",
                        "description": "test_cluster_description",
                    }
                ],
            },
        },
        "galaxies_invalid_cluster_json": {
            "list_files": ["galaxies/test_galaxy.json"],
            "list_directories": ["objects/test_name"],
            "manifest": None,
            "galaxy_json": {
                "uuid": "0179fb98-9a25-403a-bbcf-17876dbe7339",
                "name": "test_name",
                "type": "test_galaxy",
                "description": "test_galaxy_description",
                "version": 1,
            },
            "cluster_json": "not-valid-json{{{",
        },
        "taxonomies": {
            "list_files": ["taxonomies/test_namespace/machinetag.json"],
            "list_directories": ["objects/test_name"],
            "manifest": {"taxonomies": [{"name": "test_namespace"}]},
            "taxonomy_json": {
                "namespace": "test_namespace",
                "description": "test_description",
                "version": 1,
                "exclusive": True,
                "predicates": [
                    {
                        "value": "test_predicate_value",
                        "expanded": "test_predicate_expanded",
                        "colour": "test_pc",
                        "description": "test_predicate_description",
                        "exclusive": True,
                        "numerical_value": 1,
                    }
                ],
                "values": [
                    {
                        "predicate": "test_predicate_value",
                        "entry": [
                            {
                                "value": "test_entry_value",
                                "expanded": "test_entry_expanded",
                                "colour": "test_ec",
                                "description": "test_entry_description",
                                "numerical_value": 1,
                            }
                        ],
                    }
                ],
            },
        },
        "taxonomies_predicate_only": {
            "list_files": ["taxonomies/test_namespace/machinetag.json"],
            "list_directories": ["objects/test_name"],
            "manifest": {"taxonomies": [{"name": "test_namespace"}]},
            "taxonomy_json": {
                "namespace": "test_namespace",
                "description": "test_description",
                "version": 1,
                "exclusive": True,
                "predicates": [
                    {
                        "value": "test_predicate_value",
                        "expanded": "test_predicate_expanded",
                        "colour": "test_pc",
                        "description": "test_predicate_description",
                        "exclusive": True,
                        "numerical_value": 1,
                    }
                ],
                "values": [],
            },
        },
        "taxonomies_missing_manifest": {
            "list_files": ["taxonomies/test_namespace/machinetag.json"],
            "list_directories": ["objects/test_name"],
            "manifest": None,
        },
        "taxonomies_invalid_json": {
            "list_files": ["taxonomies/test_namespace/machinetag.json"],
            "list_directories": ["objects/test_name"],
            "manifest": {"taxonomies": [{"name": "test_namespace"}]},
            "taxonomy_json": "not-valid-json{{{",
        },
        "taxonomies_missing_taxonomy": {
            "list_files": ["taxonomies/test_namespace/machinetag.json"],
            "list_directories": ["objects/test_name"],
            "manifest": {"taxonomies": [{"name": "test_namespace"}]},
            "taxonomy_json": None,
        },
        "object_templates": {
            "list_files": ["objects/test_name/definition.json"],
            "list_directories": ["objects/test_name"],
            "manifest": None,
            "object_template_json": {
                "uuid": "b61d8aa7-9a0a-4b1b-b4c4-eba26fbd9628",
                "name": "test_name",
                "meta-category": "file",
                "description": "test_description",
                "version": 1,
                "required": ["test_required_1", "test_required_2"],
                "requiredOneOf": ["test_requiredOneOf_1", "test_requiredOneOf_2"],
                "attributes": {
                    "test_element": {
                        "misp-attribute": "other",
                        "ui-priority": 1,
                        "categories": ["Antivirus detection", "Other"],
                        "sane_default": ["test_sane_default_1", "test_sane_default_2"],
                        "values_list": ["test_value_1", "test_value_2"],
                        "description": "test_element_description",
                        "disable_correlation": True,
                        "multiple": True,
                    }
                },
            },
        },
        "object_templates_missing_objects_folder": {
            "list_files": ["objects/test_name/definition.json"],
            "list_directories": [],
            "manifest": None,
        },
        "object_templates_invalid_json": {
            "list_files": ["objects/test_name/definition.json"],
            "list_directories": ["objects/test_name"],
            "manifest": None,
            "object_template_json": "not-valid-json{{{",
        },
    }

    def __init__(self, repository_name: str, branch_name: str | None = None) -> None:
        if repository_name == "invalid" or branch_name == "invalid":
            raise AttributeError("Cannot access specified GitHub repository or branch")

        self._repo_name = repository_name
        self._branch_name = branch_name or "main"
        # PyGithub's repository.name returns just the repo name, not owner/repo
        short_name = repository_name.split("/")[-1]
        self.repository = SimpleNamespace(name=short_name)
        self.branch = SimpleNamespace(name=self._branch_name)
        self.url_template = self._GITHUB_RAW_TEMPLATE.format(repository_name, self._branch_name)

        data = self.BRANCH_DATA.get(self._branch_name)
        if data is None:
            raise AttributeError("Cannot access specified GitHub repository or branch")
        self._data = data

    def get_raw_url(self) -> str:
        return self.url_template

    def list_files(self, path: str) -> list[str] | None:
        files = self._data.get("list_files") or []
        return files if files else None

    def list_directories(self, path: str) -> list[str] | None:
        dirs = self._data.get("list_directories") or []
        return dirs if dirs else None


# Populate module-level BRANCH_DATA from the class after definition
BRANCH_DATA = MockGithubUtils.BRANCH_DATA


def _serialize(obj):
    if obj is None:
        return None
    if isinstance(obj, str):
        return obj
    return json.dumps(obj)


def make_mock_download_files(github_utils: MockGithubUtils):
    """Return an async mock download_files that serves canned JSON per URL."""

    async def _download_files(session, urls):
        data = github_utils._data
        results = []
        for url in urls:
            if "/clusters/" in url:
                payload = data.get("cluster_json")
            elif "/galaxies/" in url:
                payload = data.get("galaxy_json")
            elif "MANIFEST.json" in url:
                payload = data.get("manifest")
            elif url.endswith("machinetag.json"):
                payload = data.get("taxonomy_json")
            elif url.endswith("definition.json"):
                payload = data.get("object_template_json")
            else:
                payload = None

            if payload is None:
                results.append(_make_response(url, "", status_code=404))
            else:
                results.append(_make_response(url, _serialize(payload), status_code=200))
        return results

    return _download_files


def make_mock_async_client(github_utils: MockGithubUtils):
    """Return a mock httpx.AsyncClient whose .get serves MANIFEST.json."""

    async def _get(url, *args, **kwargs):
        data = github_utils._data
        if "MANIFEST.json" in url:
            payload = data.get("manifest")
            if payload is None:
                return _make_response(url, "", status_code=404)
            return _make_response(url, json.dumps(payload), status_code=200)
        return _make_response(url, "", status_code=404)

    client = MagicMock()
    client.get = AsyncMock(side_effect=_get)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    return client
