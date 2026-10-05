"""Lazy Worker proxy to avoid asyncio.get_event_loop() at import time."""

from collections.abc import Callable
from typing import Any, Protocol, cast

from streaq import Worker
from streaq.task import RegisteredTask


class EnqueueableTask(Protocol):
    """Protocol for objects that can be enqueued (RegisteredTask or lazy proxy)."""

    async def enqueue(self, *args: Any, **kwargs: Any) -> Any: ...


class _LazyTaskDecorator:
    """Decorator returned by LazyWorker.task() that defers Worker creation.

    The decorated function is wrapped so that the real streaq task registration
    only happens on first call, not at module import time.
    """

    def __init__(self, lazy_worker: "LazyWorker", func: Callable[..., Any], args: tuple, kwargs: dict) -> None:
        self._lazy_worker = lazy_worker
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._registered: RegisteredTask[Any, Any, Any] | None = None

    def _ensure_registered(self) -> RegisteredTask[Any, Any, Any]:
        if self._registered is None:
            worker = self._lazy_worker._get_worker()
            decorator = cast(Any, worker.task)(*self._args, **self._kwargs)
            self._registered = decorator(self._func)
        return self._registered

    async def enqueue(self, *args: Any, **kwargs: Any) -> Any:
        return await self._ensure_registered().enqueue(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._ensure_registered(), name)


class LazyWorker:
    """Proxy that creates a streaq Worker on first attribute access.

    streaq's Worker.__init__ calls asyncio.get_event_loop(), which raises
    RuntimeError when no event loop exists yet (e.g. during pytest collection
    or module import). This proxy defers Worker creation until it is actually
    used at runtime, when an event loop is available.
    """

    def __init__(self, redis_url: str, queue_name: str) -> None:
        self._redis_url = redis_url
        self._queue_name = queue_name
        self._worker: Worker | None = None

    def _get_worker(self) -> Worker:
        if self._worker is None:
            self._worker = Worker(redis_url=self._redis_url, queue_name=self._queue_name)
        return self._worker

    def task(self, *args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], _LazyTaskDecorator]:
        """Return a lazy decorator that defers Worker creation to first call."""

        def decorator(func: Callable[..., Any]) -> _LazyTaskDecorator:
            return _LazyTaskDecorator(self, func, args, kwargs)

        return decorator

    def __getattr__(self, name: str) -> Any:
        return getattr(self._get_worker(), name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ("_redis_url", "_queue_name", "_worker"):
            super().__setattr__(name, value)
        else:
            setattr(self._get_worker(), name, value)

    async def __aenter__(self) -> Worker:
        worker = self._get_worker()
        return await worker.__aenter__()

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Any:
        return await self._get_worker().__aexit__(exc_type, exc_val, exc_tb)

    def __repr__(self) -> str:
        state = "initialized" if self._worker is not None else "lazy"
        return f"LazyWorker(queue_name={self._queue_name!r}, {state})"
