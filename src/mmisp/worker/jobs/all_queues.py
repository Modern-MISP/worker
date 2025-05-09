import importlib.resources
import itertools

from streaq import Worker

jobs_pkg = "mmisp.worker.jobs"

all_jobs_pkgs = list(
    i.name
    for i in importlib.resources.files(jobs_pkg).iterdir()
    if i.is_dir() and all([i.joinpath("__init__.py").is_file(), i.joinpath("queue.py").is_file()])
)
jobs_pkg_names = map(".".join, zip(itertools.repeat(jobs_pkg), all_jobs_pkgs, itertools.repeat("queue")))

all_queues: dict[str, Worker] = {}

for job in all_jobs_pkgs:
    m = ".".join([jobs_pkg, job, "queue"])
    module = importlib.import_module(m)
    all_queues[job] = module.queue
