import signal
import sys

import uvicorn
from fastapi import FastAPI

from mmisp.worker.api.job_router import job_router
from mmisp.worker.api.worker_router import worker_router
from mmisp.worker.api.worker_router.input_data import WorkerEnum
from mmisp.worker.controller.worker_controller import WorkerController
from mmisp.worker.system_config_data import SystemConfigData

"""
The main module of the MMISP Worker application.
"""

app: FastAPI = FastAPI()
"""The FastAPI instance."""

app.include_router(job_router.job_router)
app.include_router(worker_router.worker_router)


def main():
    """
    The entry point of the MMISP Worker application.
    Starts the enabled workers and sets up the API.
    """

    # TODO: Remove before release
    # test.run()

    # To monitor celery workers at http://localhost:5555 uncomment the following lines.
    # Requires 'pip install flower'
    # from mmisp.worker.controller.celery_client import celery_client
    # subprocess.Popen(f'celery -A {celery_client.__name__}:celery_client flower', shell=True)

    config: SystemConfigData = SystemConfigData()
    config.read_from_env()

    for worker in WorkerEnum:
        if config.is_autostart_for_worker_enabled(worker):
            WorkerController.enable_worker(worker)

    uvicorn.run(f"{__name__}:app", port=config.api_port, log_level="info")


def interrupt_handler(signum, frame) -> None:
    sys.exit(130)


def terminate_handler(signum, frame) -> None:
    sys.exit(143)


if __name__ == "__main__":
    # signal.signal(signal.SIGINT, interrupt_handler)
    signal.signal(signal.SIGTERM, terminate_handler)
    main()
