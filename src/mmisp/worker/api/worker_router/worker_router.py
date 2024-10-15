from fastapi import APIRouter, Depends

from mmisp.worker.api.api_verification import verified
from mmisp.worker.controller import worker_controller

"""
Encapsulates API calls for worker
"""


worker_router: APIRouter = APIRouter(prefix="/worker")

"""
Every method in this file is a route for the worker_router
every endpoint is prefixed with /worker and requires the user to be verified
"""


@worker_router.get("/list_all_queues", dependencies=[Depends(verified)])
async def list_all_queues() -> dict:
    return worker_controller.inspect_active_queues()
