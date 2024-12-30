import json
import logging
import platform
from subprocess import Popen

from celery.app.control import Control
from sqlalchemy.future import select

from mmisp.api_schemas.worker import GetWorkerJobqueue, GetWorkerJobs, GetWorkerReturningJobs, GetWorkerWorkers
from mmisp.db.database import Session
from mmisp.db.models.tasks import Tasks
from mmisp.worker.api.requests_schemas import JobEnum
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.misp_database.mmisp_redis import MMispRedis

log = logging.getLogger(__name__)


"""
Encapsulates the logic of the API for the worker router
"""

__worker_processes: dict[JobEnum, set[Popen]] = {worker: set() for worker in JobEnum}
__NOW_ENABLED: str = "{worker_name}-Worker now enabled"
__ALREADY_ENABLED: str = "{worker_name}-Worker already enabled"
__STOPPED_SUCCESSFULLY: str = "{worker_name}-Worker stopped successfully"
__ALREADY_STOPPED: str = "{worker_name}-Worker was already stopped"


def is_worker_active(name: JobEnum) -> bool:
    """
    Checks if the specified worker is active.

    Args:
        name (JobEnum): The name of the worker.

    Returns:
        bool: True if the worker is active, otherwise False.

    """
    # _TaskInfo is not defined in the celery package
    report: dict[str, list[dict]] = celery_app.control.inspect().active()  # type: ignore

    if report:
        return bool(report.get(f"{name.value}@{platform.node()}"))
    return False


async def get_job_count(name: str) -> int:
    """
    Returns the number of jobs in the specified worker queue.

    Args:
        name (str): The name of the worker.

    Returns:
        int: The number of jobs in the worker's queue.

    """
    job_count: int = 0

    # _TaskInfo is not defined in the celery package
    reserved_tasks: dict[str, list[dict]] = celery_app.control.inspect().reserved()  # type: ignore
    if reserved_tasks and name in reserved_tasks:
        job_count += len(reserved_tasks[name])

    # currently executed jobs
    activ_tasks: dict[str, list[dict]] = celery_app.control.inspect().active()  # type: ignore
    if activ_tasks and name in activ_tasks:
        job_count += len(activ_tasks[name])

    activ_queues = get_worker_queues(name)
    for queue in activ_queues:
        job_count += await MMispRedis().get_enqueued_celery_tasks(queue)
    return job_count


def inspect_active_queues():  # noqa
    """
    Returns all active queues of all workers by worker name.

    Returns:
        dict[str, list[_QueueInfo]] | None: The active queues of all workers with the workername as key,
        or None if no active queues are found.

    """
    return Control(celery_app).inspect().active_queues()


def pause_worker(**kwargs) -> None:
    """
    Pauses a worker by removing all queues from the workers specified in the names list,
    preventing jobs from being executed. If names not set than all workers are addressed.

    Args:
        **kwargs: The names of the workers as a list[str].
    """
    workers = kwargs.get("names", [])
    Control(celery_app).broadcast("pause_consume_from_all_queues", destination=workers)


def reset_worker_queues(**kwargs) -> None:
    """
    Adds all queues back to the worker specified in the names list.
    If names not set than all workers are addressed.

    Args:
         **kwargs: The names of the workers as a list[str].
    """
    workers = kwargs.get("names", [])
    Control(celery_app).broadcast("reset_worker_queues", destination=workers)


def get_worker_queues(name: str) -> list[str]:
    """
    Returns the active queues of the specified worker.
    Exept the default 'celery' queue which is for controlling the workers

    Args:
        name (str): The name of the worker.

    Returns:
        list[str]: A list of active queues for the worker, excluding the default 'celery' queue.

    """
    all_used_queues = Control(celery_app).inspect().active_queues()
    if all_used_queues is None:
        return []
    all_used_queues = all_used_queues[name]
    all_used_queues = [queue["name"] for queue in all_used_queues]
    all_used_queues.remove("celery")  # remove celery queue because it is for controlling the workers
    return all_used_queues


async def get_worker_returning_jobs(db: Session) -> list[GetWorkerReturningJobs]:
    """
    Returns the returning jobs of the specified worker.

    Args:
        db (Session): The database session.

    Returns:
        list[GetWorkerReturningJobs]: A list of returning jobs for the worker.

    """
    returningJobs: list[GetWorkerReturningJobs] = []
    job_query = select(Tasks)
    jobs_result = await db.execute(job_query)
    jobs_result = jobs_result.fetchall()
    for job in jobs_result:
        returningJobs.append(
            GetWorkerReturningJobs(name=job[0].type, info=job[0].description, nextExecution=job[0].next_execution_time)
        )
    return returningJobs


def add_queue_to_worker(id: str, queue_name: str) -> None:
    """
    Adds a queue to the worker specified by the id.

    Args:
        id (str): The id of the worker.
        queue_name (str): The name of the queue to be added.

    Returns:
        None
    """
    Control(celery_app).add_consumer(queue=queue_name, destination=[id])


def remove_queue_from_worker(id: str, queue_name: str) -> None:
    """
    Removes a queue from the worker specified by the id.

    Args:
        id (str): The id of the worker.
        queue_name (str): The name of the queue to be removed.

    Returns:
        None

    """
    Control(celery_app).cancel_consumer(queue=queue_name, destination=[id])


def clear_queues() -> None:
    """
    Deletes all jobs from all queues.

    Raises:
        WorkerControllerException: If there is an issue with clearing all or some queues.
    """
    Control(celery_app).purge()  # delete all jobs from all queues
    # info with redis a single queue can be cleared


async def get_worker_list() -> list[GetWorkerWorkers]:
    """
    Retrieves a list of all workers along with their status, queues, and job count.

    Returns:
        list[GetWorkerWorkers]: A list of worker objects with their status, queues, and job counts.

    """
    user_list_computed: list[GetWorkerWorkers] = []
    activ_queues = inspect_active_queues()
    if activ_queues is None:
        return []
    for worker in list(activ_queues.keys()):
        all_queues = activ_queues[worker]
        all_queues = [queue["name"] for queue in all_queues]
        all_queues.remove("celery")  # remove celery queue because it is for controlling the workers
        count = await get_job_count(worker)
        user_list_computed.append(
            GetWorkerWorkers(
                name=worker, status="active" if count > 0 else "inactive", queues=all_queues, jobCount=count
            )
        )
    return user_list_computed


async def get_worker_jobs(name: str) -> list[GetWorkerJobs]:
    """
    Get a list of all jobs for the worker specified by the id.

    Args:
        name (str): The id of the worker.

    Returns:
        list[GetWorkerJobs]: A list of jobs for the worker.

    """
    jobs: list[GetWorkerJobs] = []
    for queue in get_worker_queues(name):
        # read jobs from redis db
        for x, task in enumerate(await MMispRedis().get_enqueued_celery_jobs(queue)):
            infos = json.loads(task)
            jobs.append(GetWorkerJobs(name=infos["headers"]["task"], placeInQueue=x + 2, queueName=queue))
            # add two because 0 ,1 are reserved for running and internal queue
    # read jobs from worker cache
    inspector = celery_app.control.inspect()
    reserved_tasks = inspector.reserved()
    if reserved_tasks and name in reserved_tasks:
        reserved_tasks = reserved_tasks[name]
    else:
        reserved_tasks = []
    # type list of entrys with name field, set queue as internal and pos in queue as 1
    # read currently executed jobs
    activ_tasks = inspector.active()
    if activ_tasks and name in activ_tasks:
        activ_tasks = activ_tasks[name]
    else:
        activ_tasks = []
    # type list of entrys with name field, set queue as internal and pos in queue as 0
    # sort by the placeInQueue for the correct order
    worker_queue_jobs: list[GetWorkerJobs] = []
    for task in activ_tasks:
        worker_queue_jobs.append(GetWorkerJobs(name=task["name"], placeInQueue=0, queueName="running"))
    for task in reserved_tasks:
        worker_queue_jobs.append(GetWorkerJobs(name=task["name"], placeInQueue=1, queueName="internal"))
    jobs = sorted(jobs, key=lambda x: (x.placeInQueue, x.queueName))
    if jobs:
        worker_queue_jobs.extend(jobs)
    return worker_queue_jobs


def get_worker_jobqueues(name: str) -> list[GetWorkerJobqueue]:
    """
    Get a list of all job queues for the worker specified by the id.

    Args:
        name (str): The id of the worker.

    Returns:
        list[GetWorkerJobqueue]: A list of job queue objects for the worker.

    """
    jobqueus: list[GetWorkerJobqueue] = []
    activ_queues = get_worker_queues(name)
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
    # pings the worker to check if it exists
    return Control(celery_app).inspect().ping([name]) is None
