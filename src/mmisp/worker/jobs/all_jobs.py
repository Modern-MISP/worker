import importlib.resources
import itertools

jobs_pkg = "mmisp.worker.jobs"

all_jobs_pkgs = list(
    i.name
    for i in importlib.resources.files(jobs_pkg).iterdir()
    if i.is_dir() and all([i.joinpath("__init__.py").is_file(), i.joinpath("fastapi_endpoints.py").is_file()])
)
jobs_pkg_names = map(".".join, zip(itertools.repeat(jobs_pkg), all_jobs_pkgs, itertools.repeat("fastapi_endpoints")))

for m in jobs_pkg_names:
    importlib.import_module(m)
