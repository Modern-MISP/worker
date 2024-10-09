import importlib
import importlib.resources
import itertools

jobs_pkg = "mmisp.worker.jobs"

all_jobs_pkgs = (
    i.name for i in importlib.resources.files(jobs_pkg).iterdir() if i.is_dir() and any(i.glob("__init__.py"))
)
jobs_pkg_names = map(".".join, zip(itertools.repeat(jobs_pkg), all_jobs_pkgs))

for m in jobs_pkg_names:
    importlib.import_module(m)
