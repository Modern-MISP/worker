from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response

from mmisp.api_schemas.worker import (
    GetWorkerJobqueue,
    GetWorkerJobs,
    GetWorkerReturningJobs,
    GetWorkerWorkers,
    RemoveAddQueueToWorker,
)
from mmisp.db.database import Session, get_db
from mmisp.worker.api.api_verification import verified
from mmisp.worker.api.requests_schemas import JobEnum
from mmisp.worker.controller import worker_controller

"""
Encapsulates API calls for worker
"""

worker_router: APIRouter = APIRouter(prefix="/worker")

"""
Every method in this file is a route for the worker_router
every endpoint is prefixed with /worker and requires the user to be verified
"""

# @worker_router.post("/clearQueue/{id}", dependencies=[Depends(verified)])
# async def clear_queue(id:str)->None:
#    pass


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
    if worker_controller.check_worker_name(id):
        raise HTTPException(status_code=404, detail=f'A worker with the name "{id}" does not exist.')
    response.headers["x-queue-name-header"] = body.queue_name
    try:  # TODO if time: also add queues added with environment variables see celery_client.py
        JobEnum(body.queue_name)
    except ValueError:
        raise HTTPException(status_code=404, detail="Queue not found")

    worker_controller.add_queue_to_worker(id, body.queue_name)


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
    if worker_controller.check_worker_name(id):
        raise HTTPException(status_code=404, detail=f'A worker with the name "{id}" does not exist.')

    response.headers["x-queue-name-header"] = body.queue_name

    queues = worker_controller.get_worker_queues(id)

    if body.queue_name not in queues:
        raise HTTPException(status_code=404, detail="Queue not found")

    if body.queue_name == "celery":
        raise HTTPException(status_code=405, detail="Celery queue cannot be removed")

    if len(queues) - 1 <= 0:
        raise HTTPException(status_code=405, detail="A worker needs to have at least one queue")

    active_state = worker_controller.inspect_active_queues()

    all_queues_in_use = []
    for key in active_state:
        if key == id:
            queues = active_state[key]
            list = [queue["name"] for queue in queues]
            list.remove(body.queue_name)
            all_queues_in_use.extend(list)
        else:
            queues = active_state[key]
            all_queues_in_use.extend([queue["name"] for queue in queues])

    if body.queue_name not in all_queues_in_use:
        raise HTTPException(status_code=406, detail="Queue after removal is not in use")

    worker_controller.remove_queue_from_worker(id, body.queue_name)


@worker_router.post("/pause/{name}", dependencies=[Depends(verified)])
async def pause_worker(name: str, response: Response) -> Response:
    """
    Pauses a single worker.

    Args:
        name (str): The name of the worker.

    Raises:
        HTTPException: If the worker name does not exist.
    """
    if worker_controller.check_worker_name(name):
        raise HTTPException(status_code=404, detail=f'A worker with the name "{id}" does not exist.')
    response.headers["x-worker-name-header"] = name  # possible to use an attribute but i am lazy feel free to change
    worker_controller.pause_worker(names=[name])


@worker_router.post("/unpause/{name}", dependencies=[Depends(verified)])
async def unpause_worker(name: str, response: Response) -> Response:
    """
    Unpauses a single worker.

    Args:
        name (str): The name of the worker.

    Raises:
        HTTPException: If the worker name does not exist.
    """
    if worker_controller.check_worker_name(name):
        raise HTTPException(status_code=404, detail=f'A worker with the name "{id}" does not exist.')
    response.headers["x-worker-name-header"] = name
    worker_controller.reset_worker_queues(names=[name])


@worker_router.get("/list_all_queues", dependencies=[Depends(verified)])
async def list_all_queues() -> dict:
    """
    Returns all active queues with the workername as key.

    Returns:
        dict: A dictionary of active queues by worker name.

    Raises:
        HTTPException: If an error occurs while retrieving the active queues.
    """
    return worker_controller.inspect_active_queues()


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
    if worker_controller.check_worker_name(id):
        raise HTTPException(status_code=404, detail=f'A worker with the name "{id}" does not exist.')

    return worker_controller.get_worker_jobqueues(id)


@worker_router.get("/jobs/{id}", dependencies=[Depends(verified)])
async def get_job(id: str) -> list[GetWorkerJobs]:
    """
    Get a list of all jobs for the worker specified by the id.

    Args:
        id (str): The id of the worker.

    Returns:
        list[GetWorkerJobs]: A list of jobs for the worker.

    Raises:
        HTTPException: If an error occurs while retrieving the jobs for the worker or the id is invalid.
    """
    if worker_controller.check_worker_name(id):
        raise HTTPException(status_code=404, detail=f'A worker with the name "{id}" does not exist.')

    return await worker_controller.get_worker_jobs(id)


@worker_router.get("/returningJobs/", dependencies=[Depends(verified)])
async def get_returning_job(
    db: Annotated[Session, Depends(get_db)],
) -> list[GetWorkerReturningJobs]:
    """
    Get a list of all returning jobs of this worker / of the queues this worker consumes.

    Args:
        db (Session): The database session

    Returns:
        list[GetWorkerReturningJobs]: A list of returning jobs for the worker.

    Raises:
        HTTPException: If an error occurs while retrieving returning jobs for the worker.
    """
    return await worker_controller.get_worker_returning_jobs(db)
