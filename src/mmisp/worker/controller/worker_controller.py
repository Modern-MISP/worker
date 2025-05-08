import asyncio
import logging
import uuid
from collections.abc import Awaitable, Mapping
from subprocess import Popen
from typing import Dict, Literal, Self, TypeVar

from fastapi import WebSocket

from mmisp.api_schemas.worker import GetWorkerJobqueue, GetWorkerWorkers
from mmisp.worker.api.requests_schemas import JobEnum
from mmisp.worker.controller.connection_manager import ConnectionManager

_K = TypeVar("_K")
_V = TypeVar("_V")


async def gather_dict(tasks: Mapping[_K, Awaitable[_V]]) -> dict[_K, _V]:
    async def inner(key: _K, coro: Awaitable[_V]) -> tuple[_K, _V]:
        return key, await coro

    pair_tasks = (inner(key, coro) for key, coro in tasks.items())
    return dict(await asyncio.gather(*pair_tasks))


log = logging.getLogger(__name__)


"""
Encapsulates the logic of the API for the worker router
"""

__worker_processes: dict[JobEnum, set[Popen]] = {worker: set() for worker in JobEnum}
__NOW_ENABLED: str = "{worker_name}-Worker now enabled"
__ALREADY_ENABLED: str = "{worker_name}-Worker already enabled"
__STOPPED_SUCCESSFULLY: str = "{worker_name}-Worker stopped successfully"
__ALREADY_STOPPED: str = "{worker_name}-Worker was already stopped"


class ServerConnectionManager(ConnectionManager):
    def __init__(self: Self) -> None:
        super().__init__()
        self.active_connections: Dict[str, WebSocket] = {}  # client_id -> websocket

    async def connect(self: Self, websocket: WebSocket) -> str:
        await websocket.accept()
        client_id = str(uuid.uuid4())
        self.active_connections[client_id] = websocket
        return client_id

    def disconnect(self: Self, client_id: str) -> None:
        self.active_connections.pop(client_id, None)

    async def send_json(self: Self, ws: WebSocket, data: dict) -> None:  # type: ignore[override]
        await ws.send_json(data)

    async def send_msg_and_wait(  # type: ignore[override]
        self: Self, client_id: str, command: str, conversation_id: str | None = None, timeout: int = 10, **extra
    ) -> dict | Literal["Timeout"]:
        ws = self.active_connections[client_id]
        return await super().send_msg_and_wait(ws, command, conversation_id, timeout=timeout, **extra)

    async def send_all_msg_and_wait(
        self: Self, command: str, timeout: int = 10, client_ids: list[str] | None = None, **extra
    ) -> dict[str, dict | Literal["Timeout"]]:
        if client_ids is None:
            client_ids = list(self.active_connections.keys())
        res = {}
        for client_id in client_ids:
            res[client_id] = self.send_msg_and_wait(client_id, command, conversation_id=None, timeout=timeout, **extra)
        return await gather_dict(res)


connection_manager = ServerConnectionManager()


async def ping() -> None:
    await connection_manager.send_all_msg_and_wait("ping")


async def pause_worker(**kwargs) -> None:
    """
    Pauses a worker by removing all queues from the workers specified in the names list,
    preventing jobs from being executed. If names not set than all workers are addressed.

    Args:
        **kwargs: The names of the workers as a list[str].
    """
    workers = kwargs.get("names", None)
    await connection_manager.send_all_msg_and_wait("remove_all_queues", client_ids=workers)


async def reset_worker_queues(**kwargs) -> None:
    """
    Adds all queues back to the worker specified in the names list.
    If names not set than all workers are addressed.

    Args:
         **kwargs: The names of the workers as a list[str].
    """
    workers = kwargs.get("names", None)
    await connection_manager.send_all_msg_and_wait("reset_queues", client_ids=workers)


async def get_worker_queues(name: str) -> list[str]:
    """
    Returns the active queues of the specified worker.

    Args:
        name (str): The name of the worker.

    Returns:
        list[str]: A list of active queues for the worker

    """
    answer = await connection_manager.send_msg_and_wait(name, "currently_listened_queues")
    if answer == "Timeout":
        raise RuntimeError("Connection to node timeout")
    return answer["msg"]


async def add_queue_to_worker(id: str, queue_name: str) -> None:
    """
    Adds a queue to the worker specified by the id.

    Args:
        id (str): The id of the worker.
        queue_name (str): The name of the queue to be added.

    Returns:
        None
    """
    answer = await connection_manager.send_msg_and_wait(id, "add_queue", queue_name=queue_name)
    if answer == "Timeout":
        raise RuntimeError("Connection to node timeout")
    return answer["msg"]


async def remove_queue_from_worker(id: str, queue_name: str) -> None:
    """
    Removes a queue from the worker specified by the id.

    Args:
        id (str): The id of the worker.
        queue_name (str): The name of the queue to be removed.

    Returns:
        None

    """
    answer = await connection_manager.send_msg_and_wait(id, "remove_queue", queue_name=queue_name)
    if answer == "Timeout":
        raise RuntimeError("Connection to node timeout")
    return answer["msg"]


async def get_worker_list() -> list[GetWorkerWorkers]:
    """
    Retrieves a list of all workers along with their status, queues, and job count.

    Returns:
        list[GetWorkerWorkers]: A list of worker objects with their status, queues, and job counts.

    """
    print(connection_manager.active_connections.keys())
    worker_queues = await connection_manager.send_all_msg_and_wait("currently_listened_queues")
    return [
        GetWorkerWorkers(name=client_id, status="active", queues=queues["msg"], jobCount=-1)
        for client_id, queues in worker_queues.items()
        if queues != "Timeout"
    ]


async def get_worker_jobqueues(name: str) -> list[GetWorkerJobqueue]:
    """
    Get a list of all job queues for the worker specified by the id.

    Args:
        name (str): The id of the worker.

    Returns:
        list[GetWorkerJobqueue]: A list of job queue objects for the worker.

    """
    jobqueus: list[GetWorkerJobqueue] = []
    activ_queues = await get_worker_queues(name)
    for queue in JobEnum:
        if queue.value not in activ_queues:
            jobqueus.append(GetWorkerJobqueue(name=queue.value, activ="inactive"))
        else:
            jobqueus.append(GetWorkerJobqueue(name=queue.value, activ="active"))
    return jobqueus


def check_worker_name(name: str) -> bool:
    """
    Check if the worker name is valid

    Args:
        name (str): The name of the worker.

    Returns:
        bool: True if the worker name is not valid, otherwise False.

    """
    return name in connection_manager.active_connections.keys()
