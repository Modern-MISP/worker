import importlib
import importlib.resources
from collections.abc import Iterator
from typing import Any

from streaq import Worker

jobs_pkg = "mmisp.worker.jobs"

all_jobs_pkgs = list(
    i.name
    for i in importlib.resources.files(jobs_pkg).iterdir()
    if i.is_dir() and all([i.joinpath("__init__.py").is_file(), i.joinpath("queue.py").is_file()])
)


class _LazyQueues:
    """Dictionary-like container that creates Worker instances on first access.

    Avoids calling asyncio.get_event_loop() at import time (which fails when
    no event loop exists yet, e.g. during pytest collection).
    """

    def __init__(self, pkg_names: list[str]) -> None:
        self._pkg_names = pkg_names
        self._queues: dict[str, Worker] = {}

    def _get_queue(self, name: str) -> Worker:
        if name not in self._queues:
            module = importlib.import_module(f"{jobs_pkg}.{name}.queue")
            self._queues[name] = module.queue
        return self._queues[name]

    def __getitem__(self, name: str) -> Worker:
        return self._get_queue(name)

    def __contains__(self, name: str) -> bool:
        return name in self._pkg_names

    def __iter__(self) -> Iterator[str]:
        return iter(self._pkg_names)

    def __len__(self) -> int:
        return len(self._pkg_names)

    def keys(self) -> list[str]:
        return self._pkg_names

    def values(self) -> list[Worker]:
        return [self._get_queue(name) for name in self._pkg_names]

    def items(self) -> list[tuple[str, Worker]]:
        return [(name, self._get_queue(name)) for name in self._pkg_names]

    def get(self, name: str, default: Any = None) -> Any:
        if name in self._pkg_names:
            return self._get_queue(name)
        return default


all_queues: _LazyQueues = _LazyQueues(all_jobs_pkgs)
