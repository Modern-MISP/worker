from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Response, WebSocketDisconnect
from fastapi.websockets import WebSocket

from mmisp.api_schemas.worker import (
    GetWorkerJobqueue,
    GetWorkerWorkers,
    RemoveAddQueueToWorker,
)
from mmisp.worker.api.api_verification import verified
from mmisp.worker.api.requests_schemas import JobEnum
from mmisp.worker.config import system_config_data
from mmisp.worker.controller import worker_controller
from mmisp.worker.controller.worker_controller import connection_manager
from mmisp.worker.jobs.all_queues import all_queues

"""
Encapsulates API calls for worker
"""

worker_router: APIRouter = APIRouter(prefix="/worker", tags=["worker"])

"""
Every method in this file is a route for the worker_router
every endpoint is prefixed with /worker and requires the user to be verified
"""

# @worker_router.post("/clearQueue/{id}", dependencies=[Depends(verified)])
# async def clear_queue(id:str)->None:
#    pass


@worker_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    if "authorization" not in websocket.headers:
        raise HTTPException(status_code=401)
    print(websocket.headers["authorization"])
    if websocket.headers["authorization"] != f"Bearer {system_config_data.worker_api_key}":
        raise HTTPException(status_code=403)

    client_id = await connection_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            connection_manager.receive_msg(data)
    except WebSocketDisconnect:
        connection_manager.disconnect(client_id)


@worker_router.get("/ping", dependencies=[Depends(verified)])
async def ping() -> dict[str, dict | Literal["Timeout"]]:
    return await connection_manager.send_all_msg_and_wait("ping")


@worker_router.get("/queues", dependencies=[Depends(verified)])
async def get_queues() -> dict:
    queues = {}
    for name, q in all_queues.items():
        async with q:
            queues[name] = {"queue_size": await q.queue_size(), "counters": q.counters}
    return queues


@worker_router.post("/addQueue/{id}", dependencies=[Depends(verified)])
async def add_queue(id: str, body: RemoveAddQueueToWorker, response: Response) -> None:
    """
    Adds an existing queue to a worker.

    Args:
        id (str): The id of the worker.
        body (RemoveAddQueueToWorker): The request body containing the queue name to add.

    Returns:
        None

    Raises:
        HTTPException: If the worker or queue cannot be found or if an error occurs during queue addition.
    """
    if not worker_controller.check_worker_name(id):
        raise HTTPException(status_code=404, detail=f'A worker with the name "{id}" does not exist.')
    response.headers["x-queue-name-header"] = body.queue_name
    try:
        JobEnum(body.queue_name)
    except ValueError:
        raise HTTPException(status_code=404, detail="Queue not found")

    await worker_controller.add_queue_to_worker(id, body.queue_name)


@worker_router.post("/removeQueue/{id}", dependencies=[Depends(verified)])
async def remove_queue(id: str, body: RemoveAddQueueToWorker, response: Response) -> None:
    """
    Removes an existing queue from a worker.

    Args:
        id (str): The id of the worker.
        body (RemoveAddQueueToWorker): The request body containing the queue name to remove.

    Returns:
        None

    Raises:
        HTTPException: If the worker or queue cannot be found or if an error occurs during queue removal.
    """
    if not worker_controller.check_worker_name(id):
        raise HTTPException(status_code=404, detail=f'A worker with the name "{id}" does not exist.')

    response.headers["x-queue-name-header"] = body.queue_name

    queues = await worker_controller.get_worker_queues(id)

    if body.queue_name not in queues:
        raise HTTPException(status_code=404, detail="Queue not found")

    await worker_controller.remove_queue_from_worker(id, body.queue_name)


@worker_router.post("/pause/{name}", dependencies=[Depends(verified)])
async def pause_worker(name: str) -> None:
    """
    Pauses a single worker.

    Args:
        name (str): The name of the worker.

    Raises:
        HTTPException: If the worker name does not exist.
    """
    if not worker_controller.check_worker_name(name):
        raise HTTPException(status_code=404, detail=f'A worker with the name "{id}" does not exist.')
    await worker_controller.pause_worker(names=[name])


@worker_router.post("/unpause/{name}", dependencies=[Depends(verified)])
async def unpause_worker(name: str) -> None:
    """
    Unpauses a single worker.

    Args:
        name (str): The name of the worker.

    Raises:
        HTTPException: If the worker name does not exist.
    """
    if not worker_controller.check_worker_name(name):
        raise HTTPException(status_code=404, detail=f'A worker with the name "{id}" does not exist.')
    await worker_controller.reset_worker_queues(names=[name])


@worker_router.get("/list_workers", dependencies=[Depends(verified)])
async def list_all_workers() -> list[GetWorkerWorkers]:
    """
    Get a list of all workers.

    Returns:
        list[GetWorkerWorkers]: A list of GetWorkerWorkers objects with status, queues,
        and job counts of a single worker.

    Raises:
        HTTPException: If an error occurs while retrieving the worker list.
    """
    return await worker_controller.get_worker_list()


@worker_router.get("/jobqueue/{id}", dependencies=[Depends(verified)])
async def get_job_queue(id: str) -> list[GetWorkerJobqueue]:
    """
    Get a list of all job queues for the worker specified by the id.

    Args:
        id (str): The id of the worker.

    Returns:
        list[GetWorkerJobqueue]: A list of job queue objects for the worker.

    Raises:
        HTTPException: If an error occurs while retrieving the job queues or the worker id is invalid.
    """
    if not worker_controller.check_worker_name(id):
        raise HTTPException(status_code=404, detail=f'A worker with the name "{id}" does not exist.')

    return await worker_controller.get_worker_jobqueues(id)
